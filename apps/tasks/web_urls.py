from django.urls import path

from .views import (
    task_analyst_download,
    task_analyst_page,
    task_analyst_run,
    task_import_page,
    task_list_page,
)

urlpatterns = [
    path("", task_list_page, name="task-list-page"),
    path("import/", task_import_page, name="task-import-page"),
    path("analyst/", task_analyst_page, name="task-analyst-page"),
    path("analyst/run/", task_analyst_run, name="task-analyst-run"),
    path("analyst/runs/<int:run_id>/download/", task_analyst_download, name="task-analyst-download"),
]
