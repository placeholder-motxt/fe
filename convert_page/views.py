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

                fastapi_url = os.getenv("key_yang_lu_mau", "http://localhost:8000") + '/convert/'
                try:
                    fastapi_response = requests.post(
                        fastapi_url,
                        json=processed_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                except requests.exceptions.RequestException as e:
                    logger.error(f"FastAPI request failed: {e}")
                    return JsonResponse({'error': 'Failed to connect to conversion service'}, status=503)

                # Safely parse FastAPI response
                try:
                    response_data = fastapi_response.json()
                except json.JSONDecodeError:
                    logger.error("Invalid JSON response from FastAPI")
                    return JsonResponse({'error': 'Invalid response from conversion service'}, status=500)

                if fastapi_response.status_code == 200:
                    # Return ZIP file
                    django_response = HttpResponse(
                        fastapi_response.content,
                        content_type='application/zip'
                    )
                    django_response['Content-Disposition'] = f'attachment; filename="{filenames[0]}.zip"'
                    return django_response
                else:
                    return JsonResponse(response_data, status=fastapi_response.status_code)

        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error in convert_page: {str(e)}", exc_info=True)
            return JsonResponse({'error': 'Internal server error'}, status=500)

    return render(request, 'convert_page.html')