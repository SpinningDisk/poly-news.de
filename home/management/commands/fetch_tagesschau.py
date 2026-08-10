import random
from datetime import datetime

import requests
from django.core.management.base import BaseCommand

from home.ai import rewrite_article
from home.models import Article, SiteSettings

API_URL = "https://www.tagesschau.de/api2u/homepage/"

# Preference order for which image size/crop to store, falling back to
# whatever's available if none of these keys exist on a given item.
PREFERRED_IMAGE_KEYS = ["16x9-640", "16x9-432", "16x9-256", "1x1-432", "1x1-256"]


def pick_image_url(teaser_image): # get placeholder images for now
    variants = (teaser_image or {}).get("imageVariants", {})
    for key in PREFERRED_IMAGE_KEYS:
        if key in variants:
            return variants[key]
    return next(iter(variants.values()), "")


class Command(BaseCommand):
    help = "Fetches one new item from the tagesschau homepage feed and stores it as an Article."

    def handle(self, *args, **options):
        response = requests.get(
            API_URL,
            timeout=15,
            headers={"User-Agent": "PolyNewsBot/0.1"},
        )
        response.raise_for_status()
        data = response.json()

        items = data.get("news", [])
        known_ids = set(Article.objects.values_list("external_id", flat=True))
        fresh_items = [item for item in items if item.get("externalId") not in known_ids]

        if not fresh_items:
            print("Keine neuen Artikel gefunden.")
            return

        item = random.choice(fresh_items)

        event_date = (
            datetime.fromisoformat(item["date"]).date()
            if item.get("date")
            else datetime.now().date()
        )
        if not item.get("date"):
            print(f"\033[31;1mWARNING: article {item.get("title")} has no date associated; using current")

        text = f"{item.get('topline', '')} {item.get('firstSentence', '')}".strip()

        article = Article.objects.create(
            external_id=item.get("externalId") or None,
            title=item.get("title") or "Ohne Titel",
            text=text or "(kein Text verfügbar)",
            event_date=event_date,
            category=item.get("ressort", ""),
            image_url=pick_image_url(item.get("teaserImage")),
            source_url=item.get("shareURL", ""),
            is_headline=bool(item.get("breakingNews")),
            ai_processed=False,
        )

        if SiteSettings.load().ai_mode == "server":
            new_title, new_text = rewrite_article(article.title, article.text)
            article.title = new_title
            article.text = new_text
            article.ai_processed = True
            article.save()
            self.stdout.write(f"Neuer Artikel (KI-verarbeitet): {article.title}")
        else:
            self.stdout.write(
                f"Neuer Rohartikel wartet im Admin auf lokale Prüfung: {article.title}"
            )
