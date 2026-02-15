from django.conf import settings
from django.db import models

from apps.tenants.models import Tenant


class Meeting(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="meetings")
    title = models.CharField(max_length=255)
    agenda = models.TextField(blank=True)
    scheduled_for = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organized_meetings")
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="meetings", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_for"]

    def __str__(self):
        return self.title
