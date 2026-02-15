import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from office_copilot.authz import enforce_tenant_access
from apps.tasks.models import AIJob
from .models import Presentation
from .services.ai_engine import generate_presentation_from_text


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
