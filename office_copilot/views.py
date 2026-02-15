from django.shortcuts import render


def home(request):
    stats = {"tasks": 0, "meetings": 0, "reports": 0, "presentations": 0}
    if getattr(request, "tenant", None):
        tenant = request.tenant
        stats = {
            "tasks": tenant.tasks.count(),
            "meetings": tenant.meetings.count(),
            "reports": tenant.reports.count(),
            "presentations": tenant.presentations.count(),
        }
    return render(request, "dashboard/index.html", {"stats": stats})
