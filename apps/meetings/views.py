import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from office_copilot.authz import enforce_tenant_access
from .models import Meeting


@login_required
@require_http_methods(["GET", "POST"])
def meeting_list_create(request):
    enforce_tenant_access(request)

    if request.method == "GET":
        meetings = Meeting.objects.filter(tenant=request.tenant)
        return JsonResponse(
            {
                "results": [
                    {"id": m.id, "title": m.title, "scheduled_for": m.scheduled_for.isoformat()}
                    for m in meetings
                ]
            }
        )

    payload = json.loads(request.body or "{}")
    meeting = Meeting.objects.create(
        tenant=request.tenant,
        title=payload["title"],
        agenda=payload.get("agenda", ""),
        scheduled_for=datetime.fromisoformat(payload["scheduled_for"]),
        organizer=request.user,
    )
    return JsonResponse({"id": meeting.id, "title": meeting.title}, status=201)
