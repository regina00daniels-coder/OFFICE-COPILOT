from django.urls import path

from .views import presentation_download, presentation_workspace, word_to_presentation_page

urlpatterns = [
    path("", presentation_workspace, name="presentation-workspace"),
    path("word/upload/", word_to_presentation_page, name="word-to-presentation-page"),
    path("<int:presentation_id>/download/", presentation_download, name="presentation-download"),
]
