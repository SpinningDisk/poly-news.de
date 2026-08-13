from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("artikel/<slug:slug>/", views.article_detail, name="article_detail"),
    path("set-ai-mode/", views.set_ai_mode, name="set_ai_mode"),
    path("set-theme/", views.set_theme, name="set_theme"),
    path("ticker-data/", views.ticker_data, name="ticker_data"),
]
