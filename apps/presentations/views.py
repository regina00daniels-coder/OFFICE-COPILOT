import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from apps.tasks.models import AIJob
from .services.ai_engine import generate_presentation_from_text


@csrf_exempt
@login_required
def text_to_presentation(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    if not request.tenant:
        return JsonResponse({"error": "Tenant not found"}, status=400)

    data = json.loads(request.body)
    text = data.get("text")

    job = AIJob.objects.create(
        tenant=request.tenant,
        user=request.user,
        job_type="text_to_presentation",
        input_data={"text": text},
        status="processing"
    )

    slides = generate_presentation_from_text(text)

    job.output_data = {"slides": slides}
    job.status = "completed"
    job.save()

    return JsonResponse({"slides": slides})
