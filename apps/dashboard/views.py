from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from office_copilot.authz import enforce_tenant_access

from .services import get_dashboard_insights, get_dashboard_stats, get_recent_activity


@login_required
def dashboard_page(request):
    enforce_tenant_access(request)
    stats = get_dashboard_stats(request.tenant)
    context = {
        "stats": stats,
        "activity": get_recent_activity(request.tenant),
        "insights": get_dashboard_insights(request.tenant),
    }
    return render(request, "dashboard/index.html", context)


@login_required
def dashboard_summary(request):
    enforce_tenant_access(request)
    stats = get_dashboard_stats(request.tenant)

    return JsonResponse(
        {
            "tenant": stats.tenant_name,
            "total_tasks": stats.total_tasks,
            "completed_tasks": stats.completed_tasks,
            "overdue_tasks": stats.overdue_tasks,
            "upcoming_meetings": stats.upcoming_meetings,
            "total_reports": stats.total_reports,
            "total_presentations": stats.total_presentations,
            "completion_rate": stats.completion_rate,
            "data_runs_total": stats.data_runs_total,
            "data_runs_completed": stats.data_runs_completed,
            "document_runs_total": stats.document_runs_total,
            "document_runs_completed": stats.document_runs_completed,
            "data_run_success_rate": stats.data_run_success_rate,
            "doc_run_success_rate": stats.doc_run_success_rate,
        }
    )


@login_required
def dashboard_activity(request):
    enforce_tenant_access(request)
    return JsonResponse(get_recent_activity(request.tenant))


@login_required
def dashboard_insights(request):
    enforce_tenant_access(request)
    return JsonResponse(get_dashboard_insights(request.tenant))
