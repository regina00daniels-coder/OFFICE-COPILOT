from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Tenant Info", {"fields": ("tenant", "role")}),)
    list_display = ("username", "email", "tenant", "role", "is_staff")
    list_filter = ("tenant", "role", "is_staff")
