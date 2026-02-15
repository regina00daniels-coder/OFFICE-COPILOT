import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from office_copilot.authz import enforce_role, enforce_tenant_access
from .models import DataAnalysisRun, DocumentReportRun, Report
from .services import analyze_business_data, build_powerpoint_report, extract_document_text


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


@login_required
@require_http_methods(["GET"])
def reporting_workspace(request):
    enforce_tenant_access(request)
    data_runs = DataAnalysisRun.objects.filter(tenant=request.tenant).select_related("created_by")[:20]
    doc_runs = DocumentReportRun.objects.filter(tenant=request.tenant).select_related("created_by")[:20]
    return render(
        request,
        "reporting/workspace.html",
        {
            "data_runs": data_runs,
            "doc_runs": doc_runs,
            "data_result": request.session.pop("data_result", None),
            "doc_result": request.session.pop("doc_result", None),
        },
    )


@login_required
@require_http_methods(["POST"])
def data_analysis_run(request):
    enforce_role(request, {request.user.Role.ADMIN, request.user.Role.STAFF})
    upload = request.FILES.get("file")
    if not upload:
        request.session["data_result"] = {"detail": "Missing dataset upload"}
        return redirect("reporting-workspace")

    run = DataAnalysisRun.objects.create(
        tenant=request.tenant,
        created_by=request.user,
        source_file=upload,
        status=DataAnalysisRun.Status.PROCESSING,
    )
    try:
        run.source_file.open("rb")
        summary, workbook_bytes = analyze_business_data(run.source_file, run.source_file.name)
        run.source_file.close()
        filename = f"business_analysis_{run.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        run.workbook_file.save(filename, ContentFile(workbook_bytes), save=False)
        run.summary = summary
        run.status = DataAnalysisRun.Status.COMPLETED
        run.save(update_fields=["workbook_file", "summary", "status"])
        Report.objects.create(
            tenant=request.tenant,
            name=f"Business Data Analysis {run.id}",
            report_type=Report.Type.OPERATIONS,
            payload={"data_analysis_run_id": run.id, **summary},
            generated_by=request.user,
        )
        request.session["data_result"] = {"run_id": run.id, **summary}
    except Exception as exc:
        run.status = DataAnalysisRun.Status.FAILED
        run.summary = {"error": str(exc)}
        run.save(update_fields=["status", "summary"])
        request.session["data_result"] = {"detail": str(exc)}
    return redirect("reporting-workspace")


@login_required
@require_http_methods(["POST"])
def document_report_run(request):
    enforce_role(request, {request.user.Role.ADMIN, request.user.Role.STAFF})
    upload = request.FILES.get("file")
    if not upload:
        request.session["doc_result"] = {"detail": "Missing document upload"}
        return redirect("reporting-workspace")

    run = DocumentReportRun.objects.create(
        tenant=request.tenant,
        created_by=request.user,
        source_file=upload,
        status=DocumentReportRun.Status.PROCESSING,
    )
    try:
        run.source_file.open("rb")
        text = extract_document_text(run.source_file, run.source_file.name)
        run.source_file.close()
        summary, pptx_bytes = build_powerpoint_report(run.source_file.name.split("/")[-1], text)
        filename = f"document_report_{run.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pptx"
        run.powerpoint_file.save(filename, ContentFile(pptx_bytes), save=False)
        run.summary = summary
        run.status = DocumentReportRun.Status.COMPLETED
        run.save(update_fields=["powerpoint_file", "summary", "status"])
        Report.objects.create(
            tenant=request.tenant,
            name=f"Document Report Deck {run.id}",
            report_type=Report.Type.OPERATIONS,
            payload={"document_report_run_id": run.id, **summary},
            generated_by=request.user,
        )
        request.session["doc_result"] = {"run_id": run.id, **summary}
    except Exception as exc:
        run.status = DocumentReportRun.Status.FAILED
        run.summary = {"error": str(exc)}
        run.save(update_fields=["status", "summary"])
        request.session["doc_result"] = {"detail": str(exc)}
    return redirect("reporting-workspace")


@login_required
@require_http_methods(["GET"])
def data_run_download(request, run_id):
    enforce_tenant_access(request)
    run = get_object_or_404(DataAnalysisRun, id=run_id, tenant=request.tenant)
    if not run.workbook_file:
        return JsonResponse({"detail": "No workbook generated for this run"}, status=404)
    run.workbook_file.open("rb")
    payload = run.workbook_file.read()
    run.workbook_file.close()
    response = HttpResponse(
        payload,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    name = run.workbook_file.name.split("/")[-1]
    response["Content-Disposition"] = f'attachment; filename="{name}"'
    return response


@login_required
@require_http_methods(["GET"])
def doc_run_download(request, run_id):
    enforce_tenant_access(request)
    run = get_object_or_404(DocumentReportRun, id=run_id, tenant=request.tenant)
    if not run.powerpoint_file:
        return JsonResponse({"detail": "No PowerPoint generated for this run"}, status=404)
    run.powerpoint_file.open("rb")
    payload = run.powerpoint_file.read()
    run.powerpoint_file.close()
    response = HttpResponse(
        payload,
        content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
    name = run.powerpoint_file.name.split("/")[-1]
    response["Content-Disposition"] = f'attachment; filename="{name}"'
    return response
