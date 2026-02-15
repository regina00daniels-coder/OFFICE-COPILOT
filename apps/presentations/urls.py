from django.urls import path
from .views import text_to_presentation

urlpatterns = [
    path("ai/text-to-presentation/", text_to_presentation),
]
