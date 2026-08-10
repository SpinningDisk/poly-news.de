from django.contrib import admin

from .models import Article, SiteSettings


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "event_date", "is_headline", "ai_processed", "created_at")
    list_filter = ("category", "is_headline", "ai_processed")
    search_fields = ("title", "text")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("ai_mode",)

    def has_add_permission(self, request):
        # Singleton: block creating a second row from the admin.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
