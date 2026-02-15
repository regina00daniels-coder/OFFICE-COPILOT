from __future__ import annotations

from dataclasses import dataclass
from collections import Counter

from django.utils import timezone

from apps.meetings.models import Meeting
from apps.presentations.models import Presentation
from apps.reporting.models import DataAnalysisRun, DocumentReportRun, Report
from apps.reporting.ai_runtime import get_runtime_profile
from apps.tasks.models import Task
from apps.tenants.models import Tenant


@dataclass(frozen=True)
class DashboardStats:
    tenant_name: str
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    upcoming_meetings: int
    total_reports: int
    total_presentations: int
    data_runs_total: int
    data_runs_completed: int
    document_runs_total: int
    document_runs_completed: int

    @property
    def completion_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return round((self.completed_tasks / self.total_tasks) * 100, 2)

    @property
    def data_run_success_rate(self) -> float:
        if self.data_runs_total == 0:
            return 0.0
        return round((self.data_runs_completed / self.data_runs_total) * 100, 2)

    @property
    def doc_run_success_rate(self) -> float:
        if self.document_runs_total == 0:
            return 0.0
        return round((self.document_runs_completed / self.document_runs_total) * 100, 2)


def get_dashboard_stats(tenant: Tenant) -> DashboardStats:
    today = timezone.localdate()
    tasks = Task.objects.filter(tenant=tenant)
    data_runs = DataAnalysisRun.objects.filter(tenant=tenant)
    doc_runs = DocumentReportRun.objects.filter(tenant=tenant)
    return DashboardStats(
        tenant_name=tenant.name,
        total_tasks=tasks.count(),
        completed_tasks=tasks.filter(status=Task.Status.DONE).count(),
        overdue_tasks=tasks.filter(
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
            due_date__lt=today,
        ).count(),
        upcoming_meetings=Meeting.objects.filter(tenant=tenant, scheduled_for__gte=timezone.now()).count(),
        total_reports=Report.objects.filter(tenant=tenant).count(),
        total_presentations=Presentation.objects.filter(tenant=tenant).count(),
        data_runs_total=data_runs.count(),
        data_runs_completed=data_runs.filter(status=DataAnalysisRun.Status.COMPLETED).count(),
        document_runs_total=doc_runs.count(),
        document_runs_completed=doc_runs.filter(status=DocumentReportRun.Status.COMPLETED).count(),
    )


def get_recent_activity(tenant: Tenant) -> dict[str, list[dict]]:
    tasks = Task.objects.filter(tenant=tenant).order_by("-created_at")[:5]
    meetings = Meeting.objects.filter(tenant=tenant).order_by("-created_at")[:5]
    reports = Report.objects.filter(tenant=tenant).order_by("-created_at")[:5]

    return {
        "tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in tasks],
        "meetings": [{"id": m.id, "title": m.title, "scheduled_for": m.scheduled_for.isoformat()} for m in meetings],
        "reports": [{"id": r.id, "name": r.name, "type": r.report_type} for r in reports],
    }


def get_dashboard_insights(tenant: Tenant) -> dict:
    data_runs = list(DataAnalysisRun.objects.filter(tenant=tenant).order_by("-created_at")[:12])
    doc_runs = list(DocumentReportRun.objects.filter(tenant=tenant).order_by("-created_at")[:12])

    data_runs.reverse()
    doc_runs.reverse()

    data_labels = [run.created_at.strftime("%m-%d") for run in data_runs]
    cleaned_rows = [int(run.summary.get("rows_after_cleaning", 0) or 0) for run in data_runs]
    removed_rows = [int(run.summary.get("rows_removed", 0) or 0) for run in data_runs]
    outliers = [int(run.summary.get("outlier_count", run.summary.get("anomalous_due_dates", 0)) or 0) for run in data_runs]

    doc_labels = [run.created_at.strftime("%m-%d") for run in doc_runs]
    doc_slides = [int(run.summary.get("slides_generated", 0) or 0) for run in doc_runs]

    keyword_counter = Counter()
    for run in doc_runs:
        keywords = run.summary.get("top_keywords", [])
        if isinstance(keywords, list):
            keyword_counter.update(str(word) for word in keywords if str(word).strip())
    top_keywords = keyword_counter.most_common(8)

    data_total = len(data_runs)
    doc_total = len(doc_runs)
    data_ok = sum(1 for run in data_runs if run.status == DataAnalysisRun.Status.COMPLETED)
    doc_ok = sum(1 for run in doc_runs if run.status == DocumentReportRun.Status.COMPLETED)

    profile = get_runtime_profile()
    return {
        "data_quality_trend": {
            "labels": data_labels,
            "cleaned_rows": cleaned_rows,
            "rows_removed": removed_rows,
            "outliers": outliers,
        },
        "document_trend": {
            "labels": doc_labels,
            "slides": doc_slides,
        },
        "pipeline_health": {
            "data_completed": data_ok,
            "data_failed": max(data_total - data_ok, 0),
            "doc_completed": doc_ok,
            "doc_failed": max(doc_total - doc_ok, 0),
        },
        "top_keywords": {
            "labels": [item[0] for item in top_keywords],
            "counts": [item[1] for item in top_keywords],
        },
        "runtime": {
            "cpu_count": profile.cpu_count,
            "cpu_target": profile.cpu_target,
            "worker_threads": profile.worker_threads,
            "device": profile.device,
            "gpu_name": profile.gpu_name or "",
            "embedding_model": profile.embedding_model,
        },
    }
