# views.py
import json
import os
import random
import requests
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .metrics import REQUEST_LATENCY, http_requests_total
from django_ratelimit.decorators import ratelimit
import logging
import time

logger = logging.getLogger(__name__)


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@require_http_methods(["GET", "POST"])
def convert_page(request):
    if request.method == 'POST':
        with REQUEST_LATENCY.labels(method="POST").time():
            http_requests_total.labels(method="POST").inc()
            try:
                files = request.FILES.getlist('files')

                # File validation
                if not files:
                    return JsonResponse({'error': 'No files uploaded'}, status=400)

                filenames = [file.name for file in files]
                if len(filenames) != len(set(filenames)):
                    return JsonResponse({'error': 'Duplicate filenames are not allowed'}, status=400)

                processed_data = {'filename': filenames, 'content': []}

                for file in files:
                    if not file.name.lower().endswith(('.class.jet', '.sequence.jet')):
                        return JsonResponse({'error': f'Invalid file type: {file.name}'}, status=400)

                    try:
                        content = file.read().decode('utf-8')
                        processed_data['content'].append([content])
                    except json.JSONDecodeError:
                        return JsonResponse({'error': f'Invalid JSON content in file: {file.name}'}, status=400)
                    except UnicodeDecodeError:
                        return JsonResponse({'error': f'Invalid UTF-8 encoding in file: {file.name}'}, status=500)

                # FastAPI integration
                fastapi_url = os.getenv("FASTAPI_SERVICE_URL", "http://localhost:8000") + "/convert/"
                try:
                    response = requests.post(
                        fastapi_url,
                        json=processed_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )
                except requests.exceptions.RequestException as e:
                    logger.error(f"FastAPI service error: {str(e)}")
                    return JsonResponse({'error': 'Conversion service unavailable'}, status=503)

                # Validate FastAPI response
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/zip' not in content_type.lower():
                        logger.error(f"Invalid content type from FastAPI: {content_type}")
                        return JsonResponse({
                            'error': 'Invalid response format from conversion service'
                        }, status=500)

                    return HttpResponse(
                        response.content,
                        content_type='application/zip'
                    )
                else:
                    # Properly parse FastAPI's error response
                    try:
                        return JsonResponse(response.json(), status=response.status_code)
                    except json.JSONDecodeError:
                        return JsonResponse({'error': 'Invalid service response'}, status=500)

            except Exception as e:
                logger.exception("Unexpected error during conversion")
                return JsonResponse({'error': 'Internal server error'}, status=500)

    return render(request, 'convert_page.html')