from django.conf import settings
from django.db import models

from apps.tenants.models import Tenant


class Presentation(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        READY = "ready", "Ready"
        ARCHIVED = "archived", "Archived"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="presentations")
    title = models.CharField(max_length=255)
    source_text = models.TextField(blank=True)
    slide_payload = models.JSONField(default=list, blank=True)
    file = models.FileField(upload_to="presentations/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="presentations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
