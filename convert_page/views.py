import json
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

# @csrf_exempt
def convert_page(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')

        # Check for no files
        if not files:
            return JsonResponse({'error': 'No files uploaded'}, status=400)

        # Check for duplicate filenames
        filenames = [file.name for file in files]
        if len(filenames) != len(set(filenames)):
            return JsonResponse({'error': 'Duplicate filenames are not allowed'}, status=400)

        # Validate file extensions and parse content
        processed_data = {
            'filename': filenames,
            'content': []
        }

        for file in files:
            if not file.name.lower().endswith(('.class.jet', '.sequence.jet')):
                return JsonResponse({'error': f'Invalid file type: {file.name}'}, status=400)

            try:
                content = json.loads(file.read().decode('utf-8'))
                processed_data['content'].append([content])  # Match FastAPI's list-of-lists structure
            except json.JSONDecodeError:
                return JsonResponse({'error': f'Invalid JSON content in file: {file.name}'}, status=400)
            except UnicodeDecodeError:
                return JsonResponse({'error': f'Invalid UTF-8 encoding in file: {file.name}'}, status=500)

        # Forward data to FastAPI
        fastapi_response = requests.post(
            'http://localhost:8000/convert/',
            json=processed_data,
            headers={'Content-Type': 'application/json'}
        )

        # Handle FastAPI's response
        if fastapi_response.status_code == 200:
            # Stream ZIP file to client
            zip_content = fastapi_response.content
            django_response = HttpResponse(
                zip_content,
                content_type='application/zip'
            )
            django_response['Content-Disposition'] = f'attachment; filename="{filenames[0]}.zip"'
            return django_response
        else:
            try:
                error_data = fastapi_response.json()
                return JsonResponse(error_data, status=fastapi_response.status_code)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'An unknown error occurred'}, status=500)

    return render(request, 'convert_page.html')