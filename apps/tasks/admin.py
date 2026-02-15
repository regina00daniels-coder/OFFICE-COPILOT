from django.contrib import admin

from .models import AIJob, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "status", "priority", "due_date")
    list_filter = ("tenant", "status", "priority")
    search_fields = ("title", "description")


@admin.register(AIJob)
class AIJobAdmin(admin.ModelAdmin):
    list_display = ("job_type", "tenant", "user", "status", "created_at")
    list_filter = ("tenant", "status")
