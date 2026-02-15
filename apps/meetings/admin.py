from django.contrib import admin

from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "scheduled_for", "organizer")
    list_filter = ("tenant",)
    search_fields = ("title", "agenda")
