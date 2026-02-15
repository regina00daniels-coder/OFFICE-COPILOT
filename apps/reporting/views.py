import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from office_copilot.authz import enforce_role, enforce_tenant_access
from .models import Report


@login_required
@require_http_methods(["GET", "POST"])
def report_list_create(request):
    if request.method == "GET":
        enforce_tenant_access(request)
        reports = Report.objects.filter(tenant=request.tenant)
        return JsonResponse({"results": [{"id": r.id, "name": r.name, "type": r.report_type} for r in reports]})

    enforce_role(request, {request.user.Role.ADMIN, request.user.Role.STAFF})
    payload = json.loads(request.body or "{}")
    report = Report.objects.create(
        tenant=request.tenant,
        name=payload["name"],
        report_type=payload.get("report_type", Report.Type.OPERATIONS),
        payload=payload.get("payload", {}),
        generated_by=request.user,
    )
    return JsonResponse({"id": report.id, "name": report.name}, status=201)
