from django.contrib import admin

from .models import Presentation


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "status", "created_by", "created_at")
    list_filter = ("tenant", "status")
    search_fields = ("title",)
