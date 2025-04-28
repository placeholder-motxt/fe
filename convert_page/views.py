import json
import os
import re
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
            project_name = request.POST.get('project_name', '').strip()
            # Get the selected style theme
            style_theme = request.POST.get('style-theme', 'modern')
            # Get the selected framework
            framework = request.POST.get('framework', 'django')

            # Validate project name
            if not project_name:
                return JsonResponse({'error': 'Project name is required'}, status=400)
            
            # Validate project name format (alphanumeric and underscore only)
            if not re.match(r'^[a-zA-Z0-9_]+$', project_name):
                return JsonResponse({'error': 'Project name can only contain letters, numbers, and underscores'}, status=400)

            # File validation
            if not files:
                return JsonResponse({'error': 'No files uploaded'}, status=400)

            filenames = [file.name for file in files]
            if len(filenames) != len(set(filenames)):
                return JsonResponse({'error': 'Duplicate filenames are not allowed'}, status=400)

            processed_data = {
                'filename': filenames, 
                'content': [],
                'project_name': project_name,
                'style_theme': style_theme,
                'project_type': framework  # For backward compatibility
            }

            # Add group_id if framework is springboot
            if framework == 'springboot':
                group_id = request.POST.get('group_id', '').strip()
                
                # Validate group_id is not empty for springboot
                if not group_id:
                    return JsonResponse({'error': 'Group ID is required for SpringBoot projects'}, status=400)
                
                # Validate group_id contains at least one dot
                if '.' not in group_id:
                    return JsonResponse({'error': 'Group ID must contain at least one dot (e.g., com.example)'}, status=400)
                
                processed_data['group_id'] = group_id

            for file in files:
                if not file.name.lower().endswith(('.class.jet', '.sequence.jet')):
                    return JsonResponse({'error': f'Invalid file type: {file.name}'}, status=400)

                try:
                    content = file.read().decode('utf-8')
                    processed_data['content'].append([content])
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
                if 'application/zip' in content_type.lower():
                    # For ZIP files, return the binary content with appropriate headers
                    http_response = HttpResponse(
                        response.content,
                        content_type='application/zip'
                    )
                    # Add Content-Disposition header for download
                    http_response['Content-Disposition'] = f'attachment; filename="{files[0].name}.zip"'
                    return http_response
                else:
                    logger.error(f"Invalid content type from FastAPI: {content_type}")
                    return JsonResponse({
                        'error': 'Invalid response format from conversion service'
                    }, status=500)
            else:
                # Properly parse FastAPI's error response
                try:
                    return JsonResponse(response.json(), status=response.status_code, safe=False)
                except json.JSONDecodeError as ex:
                    return JsonResponse({'error': 'Invalid service response'}, status=500)

        except Exception as e:
            logger.exception("Unexpected error during conversion")
            return JsonResponse({'error': 'Internal server error'}, status=500)

    return render(request, 'convert_page.html')
