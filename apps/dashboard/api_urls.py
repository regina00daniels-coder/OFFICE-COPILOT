from django.urls import path

from .views import dashboard_activity, dashboard_insights, dashboard_summary

urlpatterns = [
    path("summary/", dashboard_summary, name="dashboard-summary"),
    path("activity/", dashboard_activity, name="dashboard-activity"),
    path("insights/", dashboard_insights, name="dashboard-insights"),
]
