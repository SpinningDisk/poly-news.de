from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

import requests

from .models import Article, SiteSettings

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
TICKER_CACHE_KEY = "ticker_quotes"
TICKER_CACHE_TTL = 60  # seconds - avoids hammering Yahoo on every visitor's scroll

_TICKER_SYMBOLS = [
    {"symbol": "NVDA", "url": "https://finance.yahoo.com/quote/NVDA"},
    {"symbol": "AAPL", "url": "https://finance.yahoo.com/quote/AAPL"},
    {"symbol": "TSLA", "url": "https://finance.yahoo.com/quote/TSLA"},
    {"symbol": "BTC-USD", "url": "https://finance.yahoo.com/quote/BTC-USD"},
    {"symbol": "SAP.DE", "url": "https://finance.yahoo.com/quote/SAP.DE"},
]


def _fetch_quote_change(symbol):
    """Returns % change vs. previous close, or None if the fetch fails."""
    try:
        response = requests.get(
            YAHOO_CHART_URL.format(symbol=symbol),
            params={"interval": "1d", "range": "1d"},
            headers={"User-Agent": "PolyNewsBot/0.1"},
            timeout=5,
        )
        response.raise_for_status()
        meta = response.json()["chart"]["result"][0]["meta"]
        price = meta["regularMarketPrice"]
        previous_close = meta.get("chartPreviousClose") or meta.get("previousClose")
        return round((price - previous_close) / previous_close * 100, 2)
    except Exception:
        return None


def _get_ticker_data():
    """
    Real quotes via Yahoo's unofficial (undocumented, no-key-needed) chart
    endpoint - same kind of caveat as the tagesschau API: it can change
    shape without notice, so any symbol that fails just shows 0.0% rather
    than breaking the whole ticker. Cached briefly since this fires every
    time any visitor's ticker scrolls out of view.
    """
    cached = cache.get(TICKER_CACHE_KEY)
    if cached is not None:
        return cached

    data = []
    for item in _TICKER_SYMBOLS:
        change = _fetch_quote_change(item["symbol"])
        data.append({"symbol": item["symbol"], "change": change if change is not None else "ERROR", "url": item["url"]})

    cache.set(TICKER_CACHE_KEY, data, TICKER_CACHE_TTL)
    return data


def ticker_data(request):
    return JsonResponse({"ticker": _get_ticker_data()})


def _nav_context(request):
    """Shared bits every page's nav needs: category list + current theme."""
    categories = (
        Article.objects.filter(ai_processed=True)
        .exclude(category="")
        .order_by("category")
        .values_list("category", flat=True)
        .distinct()
    )
    return {
        "categories": categories,
        "theme": request.COOKIES.get("theme", ""),
        "current_path": request.path,
    }


def home(request):
    category = request.GET.get("category") or None
    origin = request.GET.get("origin") or None

    articles = Article.objects.filter(ai_processed=True)
    if category:
        articles = articles.filter(category__iexact=category)
    if origin:
        articles = articles.filter(origin=origin)

    is_filtered = bool(category or origin)
    headline = None if is_filtered else (articles.filter(is_headline=True).first() or articles.first())
    other_articles = articles.exclude(pk=headline.pk) if headline else articles

    context = {
        "headline": headline,
        "articles": other_articles,
        "current_category": category,
        "current_origin": origin,
        "ticker": _get_ticker_data(),
        "ticker_repeat": range(10),
        "ai_mode": SiteSettings.load().ai_mode,
    }
    context.update(_nav_context(request))
    return render(request, "home.html", context)


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, ai_processed=True)
    context = {"article": article}
    context.update(_nav_context(request))
    return render(request, "article_detail.html", context)


@require_POST
def set_ai_mode(request):
    mode = request.POST.get("ai_mode")
    if mode in dict(SiteSettings.AI_MODE_CHOICES):
        settings_obj = SiteSettings.load()
        settings_obj.ai_mode = mode
        settings_obj.save()
    return redirect("home")


@require_POST
def set_theme(request):
    theme = request.POST.get("theme")
    next_path = request.POST.get("next") or "/"
    response = redirect(next_path)
    if theme in ("light", "dark"):
        response.set_cookie("theme", theme, max_age=60 * 60 * 24 * 365)
    return response
