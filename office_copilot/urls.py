from django.contrib import admin
from django.urls import include, path

from .views import home

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
    path("api/meetings/", include("apps.meetings.urls")),
    path("api/reporting/", include("apps.reporting.urls")),
    path("api/presentations/", include("apps.presentations.urls")),
]
