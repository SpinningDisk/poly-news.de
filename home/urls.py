from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("set-ai-mode/", views.set_ai_mode, name="set_ai_mode"),
]
