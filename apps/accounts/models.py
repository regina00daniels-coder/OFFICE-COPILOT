from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.tenants.models import Tenant


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        STAFF = "staff", "Staff"
        USER = "user", "User"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.USER)

    def __str__(self):
        return f"{self.username} ({self.tenant})"

    @property
    def can_manage_reports(self) -> bool:
        return self.is_superuser or self.role in {self.Role.ADMIN, self.Role.STAFF}
