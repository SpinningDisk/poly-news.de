from django.db import models
from django.utils.text import slugify


class Article(models.Model):
    # Core fields you asked for
    text = models.TextField(help_text="The (rewritten, satirical) article body")
    event_date = models.DateField(help_text="When the real-world event actually happened")
    category = models.CharField(max_length=50, blank=True)

    # A few extra fields that pay for themselves quickly:
    title = models.CharField(max_length=200)  # needed for {{ HEADLINE }} and card titles
    slug = models.SlugField(max_length=220, unique=True, blank=True)  # for clean article URLs later
    image_url = models.URLField(blank=True)  # header/card image
    source_url = models.URLField(blank=True, help_text="Original source article, for reference/attribution")
    is_headline = models.BooleanField(default=False, help_text="Pin this as the big top story")
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
