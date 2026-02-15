from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.meetings.models import Meeting
from apps.presentations.models import Presentation
from apps.reporting.models import Report
from apps.tasks.models import Task
from apps.tenants.models import Tenant
from .views import dashboard_page


class DashboardTests(TestCase):
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

        today = timezone.localdate()
        now = timezone.now()

        Task.objects.create(
            tenant=self.tenant_a,
            title="Done task",
            status=Task.Status.DONE,
            due_date=today - timedelta(days=2),
            created_by=self.user_a,
        )
        Task.objects.create(
            tenant=self.tenant_a,
            title="Overdue task",
            status=Task.Status.TODO,
            due_date=today - timedelta(days=1),
            created_by=self.user_a,
        )
        Task.objects.create(
            tenant=self.tenant_a,
            title="Open task",
            status=Task.Status.IN_PROGRESS,
            due_date=today + timedelta(days=2),
            created_by=self.user_a,
        )
        Task.objects.create(
            tenant=self.tenant_b,
            title="Other tenant task",
            status=Task.Status.DONE,
            due_date=today,
            created_by=self.user_b,
        )

        Meeting.objects.create(
            tenant=self.tenant_a,
            title="Upcoming meeting",
            scheduled_for=now + timedelta(days=1),
            organizer=self.user_a,
        )
        Meeting.objects.create(
            tenant=self.tenant_a,
            title="Past meeting",
            scheduled_for=now - timedelta(days=1),
            organizer=self.user_a,
        )
        Meeting.objects.create(
            tenant=self.tenant_b,
            title="Other tenant meeting",
            scheduled_for=now + timedelta(days=1),
            organizer=self.user_b,
        )

        Report.objects.create(tenant=self.tenant_a, name="Tenant A report", generated_by=self.user_a)
        Report.objects.create(tenant=self.tenant_b, name="Tenant B report", generated_by=self.user_b)

        Presentation.objects.create(tenant=self.tenant_a, title="Tenant A deck", created_by=self.user_a)
        Presentation.objects.create(tenant=self.tenant_b, title="Tenant B deck", created_by=self.user_b)

        self.client = Client()
        self.factory = RequestFactory()

    def test_dashboard_summary_is_tenant_scoped(self):
        self.client.login(username="alice", password="pass1234")
        response = self.client.get(reverse("dashboard-summary"), HTTP_X_TENANT="a.local", HTTP_HOST="localhost")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["tenant"], "Tenant A")
        self.assertEqual(payload["total_tasks"], 3)
        self.assertEqual(payload["completed_tasks"], 1)
        self.assertEqual(payload["overdue_tasks"], 1)
        self.assertEqual(payload["upcoming_meetings"], 1)
        self.assertEqual(payload["total_reports"], 1)
        self.assertEqual(payload["total_presentations"], 1)
        self.assertEqual(payload["completion_rate"], 33.33)

    def test_dashboard_activity_is_tenant_scoped(self):
        self.client.login(username="alice", password="pass1234")
        response = self.client.get(reverse("dashboard-activity"), HTTP_X_TENANT="a.local", HTTP_HOST="localhost")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        task_titles = {item["title"] for item in payload["tasks"]}
        meeting_titles = {item["title"] for item in payload["meetings"]}
        report_names = {item["name"] for item in payload["reports"]}

        self.assertIn("Done task", task_titles)
        self.assertIn("Overdue task", task_titles)
        self.assertNotIn("Other tenant task", task_titles)
        self.assertIn("Upcoming meeting", meeting_titles)
        self.assertNotIn("Other tenant meeting", meeting_titles)
        self.assertIn("Tenant A report", report_names)
        self.assertNotIn("Tenant B report", report_names)

    def test_dashboard_insights_endpoint_returns_runtime_and_trends(self):
        self.client.login(username="alice", password="pass1234")
        response = self.client.get(reverse("dashboard-insights"), HTTP_X_TENANT="a.local", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("data_quality_trend", payload)
        self.assertIn("pipeline_health", payload)
        self.assertIn("runtime", payload)
        self.assertIn("worker_threads", payload["runtime"])

    def test_dashboard_cross_tenant_access_denied(self):
        self.client.login(username="alice", password="pass1234")
        response = self.client.get(reverse("dashboard-summary"), HTTP_X_TENANT="b.local", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 403)

    def test_dashboard_summary_uses_authenticated_user_tenant_when_header_missing(self):
        self.client.login(username="alice", password="pass1234")
        response = self.client.get(reverse("dashboard-summary"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["tenant"], "Tenant A")

    def test_dashboard_page_renders(self):
        request = self.factory.get(reverse("dashboard-page"), HTTP_X_TENANT="a.local", HTTP_HOST="localhost")
        request.user = self.user_a
        request.tenant = self.tenant_a
        response = dashboard_page(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Operations Dashboard", response.content)
        self.assertIn(b"Tenant A", response.content)
