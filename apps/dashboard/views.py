from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from office_copilot.authz import enforce_tenant_access


@login_required
def dashboard_summary(request):
    enforce_tenant_access(request)
    tenant = request.tenant

    data = {
        "tenant": tenant.name,
        "tasks": tenant.tasks.count(),
        "meetings": tenant.meetings.count(),
        "reports": tenant.reports.count(),
        "presentations": tenant.presentations.count(),
    }
    return JsonResponse(data)
