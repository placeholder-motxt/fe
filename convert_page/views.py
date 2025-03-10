import json
import os
import requests
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse

@require_http_methods(["GET", "POST"])
def convert_page(request):
    if request.method == 'POST':
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
                content = json.loads(file.read().decode('utf-8'))
                processed_data['content'].append([content])
            except json.JSONDecodeError:
                return JsonResponse({'error': f'Invalid JSON content in file: {file.name}'}, status=400)
            except UnicodeDecodeError:
                return JsonResponse({'error': f'Invalid UTF-8 encoding in file: {file.name}'}, status=500)

        fastapi_response = requests.post(
            os.getenv("key_yang_lu_mau", "http://localhost:8000") + '/convert/',
            json=processed_data,
            headers={'Content-Type': 'application/json'}
        )

        if fastapi_response.status_code == 200:
            django_response = HttpResponse(
                fastapi_response.content,
                content_type='application/zip'
            )
            django_response['Content-Disposition'] = f'attachment; filename="{filenames[0]}.zip"'
            return django_response
        else:
            error_data = fastapi_response.json()
            return JsonResponse(error_data, status=fastapi_response.status_code)

    return render(request, 'convert_page.html')