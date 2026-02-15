from django.urls import path

from .views import task_export_excel, task_import_excel, task_list_create

urlpatterns = [
    path("", task_list_create, name="task-list-create"),
    path("excel/export/", task_export_excel, name="task-export-excel"),
    path("excel/import/", task_import_excel, name="task-import-excel"),
]
