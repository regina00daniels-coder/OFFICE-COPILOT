import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from office_copilot.authz import enforce_tenant_access
from .models import Task


@login_required
@require_http_methods(["GET", "POST"])
def task_list_create(request):
    enforce_tenant_access(request)

    if request.method == "GET":
        tasks = Task.objects.filter(tenant=request.tenant).select_related("assigned_to")
        return JsonResponse(
            {
                "results": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "status": t.status,
                        "priority": t.priority,
                        "assigned_to": t.assigned_to.username if t.assigned_to else None,
                    }
                    for t in tasks
                ]
            }
        )

    payload = json.loads(request.body or "{}")
    task = Task.objects.create(
        tenant=request.tenant,
        title=payload["title"],
        description=payload.get("description", ""),
        status=payload.get("status", Task.Status.TODO),
        priority=payload.get("priority", Task.Priority.MEDIUM),
        created_by=request.user,
    )
    return JsonResponse({"id": task.id, "title": task.title}, status=201)
