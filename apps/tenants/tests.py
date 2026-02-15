from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.tasks.models import Task
from .models import Tenant


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.tenant_a = Tenant.objects.create(name="Tenant A", domain="a.local")
        self.tenant_b = Tenant.objects.create(name="Tenant B", domain="b.local")
        user_model = get_user_model()
        self.user_a = user_model.objects.create_user(
            username="alice", password="pass1234", tenant=self.tenant_a, role=user_model.Role.ADMIN
        )
        self.user_b = user_model.objects.create_user(
            username="bob", password="pass1234", tenant=self.tenant_b, role=user_model.Role.USER
        )
        Task.objects.create(tenant=self.tenant_a, title="A Task", created_by=self.user_a)
        Task.objects.create(tenant=self.tenant_b, title="B Task", created_by=self.user_b)
        self.client = Client()

    def test_header_tenant_resolution_and_queryset_isolation(self):
        self.client.login(username="alice", password="pass1234")
        response = self.client.get(reverse("task-list-create"), HTTP_X_TENANT="a.local", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        payload = response.json()["results"]
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["title"], "A Task")

    def test_cross_tenant_access_denied(self):
        self.client.login(username="alice", password="pass1234")
        response = self.client.get(reverse("task-list-create"), HTTP_X_TENANT="b.local", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 403)
