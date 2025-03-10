# views.py
import json
import os
import requests
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
def convert_page(request):
    if request.method == 'POST':
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
                    content = json.loads(file.read().decode('utf-8'))
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
                    timeout=10
                )
            except requests.exceptions.RequestException as e:
                logger.error(f"FastAPI service error: {str(e)}")
                return JsonResponse({'error': 'Conversion service unavailable'}, status=503)

            # Handle FastAPI response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                logger.error("Invalid JSON response from FastAPI")
                return JsonResponse({'error': 'Invalid conversion service response'}, status=500)

            # In views.py's convert_page function
            if response.status_code == 200:
                django_response = HttpResponse(
                    response.content,
                    content_type='application/zip'
                )
                django_response['Content-Disposition'] = (
                    f'attachment; filename="{filenames[0]}.zip"'
                )
                return django_response
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