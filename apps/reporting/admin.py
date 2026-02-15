from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "report_type", "generated_by", "created_at")
    list_filter = ("tenant", "report_type")
    search_fields = ("name",)
