from django.contrib import admin

from .models import DataAnalysisRun, DocumentReportRun, Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "report_type", "generated_by", "created_at")
    list_filter = ("tenant", "report_type")
    search_fields = ("name",)


@admin.register(DataAnalysisRun)
class DataAnalysisRunAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "created_by", "status", "created_at")
    list_filter = ("tenant", "status")


@admin.register(DocumentReportRun)
class DocumentReportRunAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "created_by", "status", "created_at")
    list_filter = ("tenant", "status")
