from django.urls import path

from .views import task_list_create

urlpatterns = [
    path("", task_list_create, name="task-list-create"),
]
