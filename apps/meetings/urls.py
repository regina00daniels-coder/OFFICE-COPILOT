from django.urls import path

from .views import meeting_list_create

urlpatterns = [
    path("", meeting_list_create, name="meeting-list-create"),
]
