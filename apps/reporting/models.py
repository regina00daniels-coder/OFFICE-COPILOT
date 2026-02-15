from django.conf import settings
from django.db import models

from apps.tenants.models import Tenant


class Report(models.Model):
    class Type(models.TextChoices):
        OPERATIONS = "operations", "Operations"
        TASKS = "tasks", "Tasks"
        MEETINGS = "meetings", "Meetings"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="reports")
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=Type.choices, default=Type.OPERATIONS)
    payload = models.JSONField(default=dict, blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
