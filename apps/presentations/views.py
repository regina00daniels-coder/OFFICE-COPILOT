import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from office_copilot.authz import enforce_tenant_access
from apps.tasks.models import AIJob
from .models import Presentation
from .services.ai_engine import (
    build_powerpoint_file,
    generate_presentation_from_text,
    parse_word_document,
)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def text_to_presentation(request):
    enforce_tenant_access(request)

    data = json.loads(request.body)
    text = data.get("text", "")
    title = data.get("title", "AI Generated Presentation")

    job = AIJob.objects.create(
        tenant=request.tenant,
        user=request.user,
        job_type="text_to_presentation",
        input_data={"text": text},
        status="processing",
    )

    slides = generate_presentation_from_text(text)

    presentation = Presentation.objects.create(
        tenant=request.tenant,
        title=title,
        source_text=text,
        slide_payload=slides,
        status=Presentation.Status.READY,
        created_by=request.user,
    )

    job.output_data = {"slides": slides, "presentation_id": presentation.id}
    job.status = "completed"
    job.save(update_fields=["output_data", "status"])

    return JsonResponse({"presentation_id": presentation.id, "slides": slides})


@login_required
@require_http_methods(["GET"])
def presentation_workspace(request):
    enforce_tenant_access(request)
    presentations = Presentation.objects.filter(tenant=request.tenant).order_by("-created_at")[:30]
    return render(
        request,
        "presentations/list.html",
        {"presentations": presentations, "upload_result": request.session.pop("word_upload_result", None)},
    )


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def word_to_presentation(request):
    enforce_tenant_access(request)
    upload = request.FILES.get("file")
    if not upload:
        return JsonResponse({"detail": "Missing Word file upload"}, status=400)
    if not upload.name.lower().endswith(".docx"):
        return JsonResponse({"detail": "Only .docx is currently supported"}, status=400)

    job = AIJob.objects.create(
        tenant=request.tenant,
        user=request.user,
        job_type="word_to_presentation",
        input_data={"filename": upload.name},
        status="processing",
    )
    try:
        slides, source_text = parse_word_document(upload)
        pptx_bytes = build_powerpoint_file(f"Document Deck - {upload.name}", slides)
        presentation = Presentation.objects.create(
            tenant=request.tenant,
            title=f"Deck: {upload.name}",
            source_text=source_text[:15000],
            slide_payload=slides,
            status=Presentation.Status.READY,
            created_by=request.user,
        )
        filename = f"deck_{presentation.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pptx"
        presentation.file.save(filename, ContentFile(pptx_bytes), save=True)
        job.output_data = {"presentation_id": presentation.id, "slides": slides}
        job.status = "completed"
        job.save(update_fields=["output_data", "status"])
    except Exception as exc:
        job.status = "failed"
        job.output_data = {"error": str(exc)}
        job.save(update_fields=["status", "output_data"])
        return JsonResponse({"detail": str(exc)}, status=400)

    return JsonResponse(
        {
            "presentation_id": presentation.id,
            "slides": slides,
            "download_url": reverse("presentation-download", kwargs={"presentation_id": presentation.id}),
        },
        status=201,
    )


@login_required
@require_http_methods(["POST"])
def word_to_presentation_page(request):
    enforce_tenant_access(request)
    response = word_to_presentation(request)
    try:
        payload = json.loads(response.content.decode("utf-8"))
    except Exception:
        payload = {"detail": "Failed to parse generation response"}
    request.session["word_upload_result"] = payload
    return redirect("presentation-workspace")


@login_required
@require_http_methods(["GET"])
def presentation_download(request, presentation_id):
    enforce_tenant_access(request)
    presentation = get_object_or_404(Presentation, id=presentation_id, tenant=request.tenant)
    if not presentation.file:
        return JsonResponse({"detail": "Presentation file not available"}, status=404)
    presentation.file.open("rb")
    payload = presentation.file.read()
    presentation.file.close()
    response = HttpResponse(
        payload,
        content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
    filename = presentation.file.name.split("/")[-1]
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
