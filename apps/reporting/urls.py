from django.urls import path

from .views import report_list_create

urlpatterns = [
    path("", report_list_create, name="report-list-create"),
]
