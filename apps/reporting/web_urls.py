from django.urls import path

from .views import (
    data_analysis_run,
    data_run_download,
    doc_run_download,
    document_report_run,
    reporting_workspace,
)

urlpatterns = [
    path("", reporting_workspace, name="reporting-workspace"),
    path("data/run/", data_analysis_run, name="reporting-data-run"),
    path("data/runs/<int:run_id>/download/", data_run_download, name="reporting-data-download"),
    path("document/run/", document_report_run, name="reporting-doc-run"),
    path("document/runs/<int:run_id>/download/", doc_run_download, name="reporting-doc-download"),
]
