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


class DataAnalysisRun(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="data_analysis_runs")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="data_analysis_runs")
    source_file = models.FileField(upload_to="reporting/data_runs/source/")
    workbook_file = models.FileField(upload_to="reporting/data_runs/output/", blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PROCESSING)
    summary = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Data Analysis #{self.id}"


class DocumentReportRun(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="document_report_runs")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="document_report_runs")
    source_file = models.FileField(upload_to="reporting/doc_reports/source/")
    powerpoint_file = models.FileField(upload_to="reporting/doc_reports/output/", blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PROCESSING)
    summary = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Document Report #{self.id}"
