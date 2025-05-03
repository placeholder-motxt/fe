import json
import os
import re
import requests
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
import logging

logger = logging.getLogger(__name__)

def validate_project_name(project_name):
    """Validate the project name."""
    if not project_name:
        return {'error': 'Project name is required'}, 400
    
    if not re.match(r'^[a-zA-Z0-9_]+$', project_name):
        return {'error': 'Project name can only contain letters, numbers, and underscores'}, 400
    
    return None, None

def validate_files(files):
    """Validate the uploaded files."""
    if not files:
        return {'error': 'No files uploaded'}, 400

    filenames = [file.name for file in files]
    if len(filenames) != len(set(filenames)):
        return {'error': 'Duplicate filenames are not allowed'}, 400
    
    return filenames, None

def validate_group_id(group_id):
    """Validate the group ID for SpringBoot projects."""
    if not group_id:
        return {'error': 'Group ID is required for SpringBoot projects'}, 400
    
    if '.' not in group_id:
        return {'error': 'Group ID must contain at least one dot (e.g., com.example)'}, 400
    
    return None, None

def process_file_contents(files):
    """Process and validate the content of each file."""
    content = []
    for file in files:
        if not file.name.lower().endswith(('.class.jet', '.sequence.jet')):
            return None, {'error': f'Invalid file type: {file.name}'}, 400

        try:
            file_content = file.read().decode('utf-8')
            content.append([file_content])
        except UnicodeDecodeError:
            return None, {'error': f'Invalid UTF-8 encoding in file: {file.name}'}, 500
    
    return content, None, None

def call_conversion_service(processed_data):
    """Call the FastAPI conversion service."""
    fastapi_url = os.getenv("FASTAPI_SERVICE_URL", "http://localhost:8000") + "/convert/"
    try:
        response = requests.post(
            fastapi_url,
            json=processed_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        return response, None
    except requests.exceptions.RequestException as e:
        logger.error(f"FastAPI service error: {str(e)}")
        return None, {'error': 'Conversion service unavailable'}, 503

def handle_conversion_response(response, files):
    """Process the conversion service response."""
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
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid service response'}, status=500)

@require_http_methods(["GET", "POST"])
def convert_page(request):
    if request.method != 'POST':
        return render(request, 'convert_page.html')
    
    try:
        files = request.FILES.getlist('files')
        project_name = request.POST.get('project_name', '').strip()
        style_theme = request.POST.get('style-theme', 'modern')
        framework = request.POST.get('project_type', 'django')

        # Validate inputs
        error, status = validate_project_name(project_name)
        if error:
            return JsonResponse(error, status=status)
        
        filenames, error = validate_files(files)
        if error:
            return JsonResponse(error, status=status)

        # Prepare data structure
        processed_data = {
            'filename': filenames, 
            'content': [],
            'project_name': project_name,
            'style_theme': style_theme,
            'project_type': framework
        }

        # Add group_id if framework is springboot
        if framework == 'spring':
            group_id = request.POST.get('group_id', '').strip()
            error, status = validate_group_id(group_id)
            if error:
                return JsonResponse(error, status=status)
            processed_data['group_id'] = group_id

        # Process file contents
        content, error, status = process_file_contents(files)
        if error:
            return JsonResponse(error, status=status)
        processed_data['content'] = content

        # Call conversion service
        response, error = call_conversion_service(processed_data)
        if error:
            return JsonResponse(error[0], status=error[1])

        # Handle response
        return handle_conversion_response(response, files)

    except Exception as e:
        logger.exception("Unexpected error during conversion")
        return JsonResponse({'error': 'Internal server error'}, status=500)
