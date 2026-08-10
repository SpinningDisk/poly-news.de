from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import Article, SiteSettings

# Placeholder until a real market-data feed is wired up.
STOCK_TICKER = [
    {"symbol": "NVDA", "change": 2.5, "url": "https://finance.yahoo.com/quote/NVDA"}, # funny static stocks
    {"symbol": "AAPL", "change": -0.4, "url": "https://finance.yahoo.com/quote/AAPL"},
    {"symbol": "TSLA", "change": 1.8, "url": "https://finance.yahoo.com/quote/TSLA"},
    {"symbol": "BTC-USD", "change": -3.1, "url": "https://finance.yahoo.com/quote/BTC-USD"},
    {"symbol": "SAP.DE", "change": 0.6, "url": "https://finance.yahoo.com/quote/SAP.DE"},
]


def home(request):
    # Only ever show articles that have actually been through the satire
    # rewrite - raw fetched teasers stay invisible until then.
    articles = Article.objects.filter(ai_processed=True)
    headline = articles.filter(is_headline=True).first() or articles.first()
    other_articles = articles.exclude(pk=headline.pk) if headline else articles

    return render(
        request,
        "home.html",
        {
            "headline": headline,
            "articles": other_articles,
            "ticker": STOCK_TICKER,
            "ticker_repeat": range(10),  # how many times to repeat the ticker list, see styles.css
            "ai_mode": SiteSettings.load().ai_mode,
        },
    )


@require_POST
def set_ai_mode(request):
    mode = request.POST.get("ai_mode")
    if mode in dict(SiteSettings.AI_MODE_CHOICES):
        settings_obj = SiteSettings.load()
        settings_obj.ai_mode = mode
        settings_obj.save()
    return redirect("home")
