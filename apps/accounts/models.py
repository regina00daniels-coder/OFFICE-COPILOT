from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.tenants.models import Tenant


class User(AbstractUser):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.username} ({self.tenant})"
