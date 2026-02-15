
from django.contrib import admin
from django.urls import include, path

from .views import home

urlpatterns = [
    
    path("", home, name="home"),
    path("auth/", include("apps.accounts.urls")),
    path("admin/", admin.site.urls),
    path("dashboard/", include("apps.dashboard.urls")),
    path("tasks/", include("apps.tasks.web_urls")),
    path("reporting/", include("apps.reporting.web_urls")),
    path("presentations/", include("apps.presentations.web_urls")),
    path("api/dashboard/", include("apps.dashboard.api_urls")),
    path("api/tasks/", include("apps.tasks.urls")),
    path("api/meetings/", include("apps.meetings.urls")),
    path("api/reporting/", include("apps.reporting.urls")),
    path("api/presentations/", include("apps.presentations.urls")),
]
