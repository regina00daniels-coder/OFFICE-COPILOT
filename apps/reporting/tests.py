import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.tenants.models import Tenant


class ReportingRoleAccessTests(TestCase):
    def setUp(self):
        tenant = Tenant.objects.create(name="Tenant A", domain="a.local")
        user_model = get_user_model()
        self.staff = user_model.objects.create_user(
            username="staff", password="pass1234", tenant=tenant, role=user_model.Role.STAFF
        )
        self.member = user_model.objects.create_user(
            username="member", password="pass1234", tenant=tenant, role=user_model.Role.USER
        )
        self.client = Client()

    def test_staff_can_create_report(self):
        self.client.login(username="staff", password="pass1234")
        response = self.client.post(
            reverse("report-list-create"),
            data=json.dumps({"name": "Ops Weekly"}),
            content_type="application/json",
            HTTP_X_TENANT="a.local",
            HTTP_HOST="localhost",
        )
        self.assertEqual(response.status_code, 201)

    def test_regular_user_cannot_create_report(self):
        self.client.login(username="member", password="pass1234")
        response = self.client.post(
            reverse("report-list-create"),
            data=json.dumps({"name": "Ops Weekly"}),
            content_type="application/json",
            HTTP_X_TENANT="a.local",
            HTTP_HOST="localhost",
        )
        self.assertEqual(response.status_code, 403)
