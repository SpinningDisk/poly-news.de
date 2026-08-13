from django.db import models
from django.utils.text import Truncator, slugify


class Article(models.Model):
    ORIGIN_CHOICES = [
        ("ai", "KI-generiert"),
        ("human", "Redaktion"),
        ("user", "Nutzer-generiert"),
    ]
    ORIGIN_EMOJI = {"ai": "\U0001F916", "human": "\u270D\uFE0F", "user": "\U0001F64B"}

    # Core fields
    text = models.TextField(help_text="The (rewritten, satirical) article body")
    event_date = models.DateField(help_text="When the real-world event actually happened")
    category = models.CharField(max_length=50, blank=True)

    # Extra fields
    title = models.CharField(max_length=200)
    preview_text = models.CharField(
        max_length=100, blank=True,
        help_text="Short preview text for the home page article. Leave blank to auto-generate one from `text`.",
    )
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    image_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True, help_text="Original source article, for reference/attribution")
    external_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True,
        help_text="ID from the source API, used to avoid fetching the same item twice",
    )
    origin = models.CharField(max_length=10, choices=ORIGIN_CHOICES, default="ai")
    is_headline = models.BooleanField(default=False, help_text="Pin this as the big top story")
    ai_processed = models.BooleanField(
        default=False,
        help_text="Has this gone through the satire rewrite yet? Unprocessed articles are hidden from the public site.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-event_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "artikel"
            slug = base
            n = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def preview(self):
        if self.preview_text:
            return self.preview_text
        return Truncator(self.text).words(25, truncate=" \u2026")

    @property
    def origin_label(self):
        return f"{self.ORIGIN_EMOJI.get(self.origin, '')} {self.get_origin_display()}".strip()


class SiteSettings(models.Model):
    """Singleton (always pk=1): site-wide switches that the fetch job reads."""

    AI_MODE_CHOICES = [
        ("server", "Server-KI (automatisch)"),
        ("local", "Lokale Prüfung (manuell im Admin)"),
    ]
    ai_mode = models.CharField(max_length=10, choices=AI_MODE_CHOICES, default="server")

    class Meta:
        verbose_name = "Site-Einstellung"
        verbose_name_plural = "Site-Einstellungen"

    def __str__(self):
        return f"Site-Einstellungen ({self.get_ai_mode_display()})"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
