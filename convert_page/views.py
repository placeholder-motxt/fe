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
        return {'valid': False, 'error': 'Project name is required'}
    
    if not re.match(r'^[a-zA-Z0-9_]+$', project_name):
        return {'valid': False, 'error': 'Project name can only contain letters, numbers, and underscores'}
    
    return {'valid': True}

def validate_group_id(group_id):
    """Validate the Spring group ID."""
    if not group_id:
        return {'valid': False, 'error': 'Group ID is required for SpringBoot projects'}
    
    if '.' not in group_id:
        return {'valid': False, 'error': 'Group ID must contain at least one dot (e.g., com.example)'}
    
    return {'valid': True}

def validate_files(files):
    """Validate uploaded files."""
    if not files:
        return {'valid': False, 'error': 'No files uploaded'}
    
    filenames = [file.name for file in files]
    if len(filenames) != len(set(filenames)):
        return {'valid': False, 'error': 'Duplicate filenames are not allowed'}
    
    for file in files:
        if not file.name.lower().endswith(('.class.jet', '.sequence.jet')):
            return {'valid': False, 'error': f'Invalid file type: {file.name}'}
    
    return {'valid': True, 'filenames': filenames}

def process_files(files):
    """Process uploaded files and extract content."""
    contents = []
    for file in files:
        try:
            content = file.read().decode('utf-8')
            contents.append([content])
        except UnicodeDecodeError:
            return {'success': False, 'error': f'Invalid UTF-8 encoding in file: {file.name}'}
    
    return {'success': True, 'contents': contents}

def send_to_conversion_service(data):
    """Send data to FastAPI conversion service."""
    fastapi_url = os.getenv("FASTAPI_SERVICE_URL", "http://localhost:8000") + "/convert/"
    try:
        response = requests.post(
            fastapi_url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        return {'success': True, 'response': response}
    except requests.exceptions.RequestException as e:
        logger.error(f"FastAPI service error: {str(e)}")
        return {'success': False, 'error': 'Conversion service unavailable', 'status': 503}

def handle_conversion_response(response, filename):
    """Process the response from the conversion service."""
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        if 'application/zip' in content_type.lower():
            http_response = HttpResponse(
                response.content,
                content_type='application/zip'
            )
            http_response['Content-Disposition'] = f'attachment; filename="{filename}.zip"'
            return {'success': True, 'response': http_response}
        else:
            logger.error(f"Invalid content type from FastAPI: {content_type}")
            return {
                'success': False, 
                'error': 'Invalid response format from conversion service', 
                'status': 500
            }
    else:
        try:
            return {'success': False, 'json_response': response.json(), 'status': response.status_code}
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Invalid service response', 'status': 500}

@require_http_methods(["GET", "POST"])
def convert_page(request):
    if request.method != 'POST':
        return render(request, 'convert_page.html')
    
    try:
        # Extract request data
        files = request.FILES.getlist('files')
        project_name = request.POST.get('project_name', '').strip()
        style_theme = request.POST.get('style-theme', 'modern')
        framework = request.POST.get('project_type', 'django')
        
        # Validate project name
        validation = validate_project_name(project_name)
        if not validation['valid']:
            return JsonResponse({'error': validation['error']}, status=400)
        
        # Validate files
        file_validation = validate_files(files)
        if not file_validation['valid']:
            return JsonResponse({'error': file_validation['error']}, status=400)
        
        # Process files
        processing_result = process_files(files)
        if not processing_result['success']:
            return JsonResponse({'error': processing_result['error']}, status=500)
        
        # Prepare data for conversion
        processed_data = {
            'filename': file_validation['filenames'],
            'content': processing_result['contents'],
            'project_name': project_name,
            'style_theme': style_theme,
            'project_type': framework
        }
        
        # Add group_id for Spring framework
        if framework == 'spring':
            group_id = request.POST.get('group_id', '').strip()
            group_validation = validate_group_id(group_id)
            if not group_validation['valid']:
                return JsonResponse({'error': group_validation['error']}, status=400)
            processed_data['group_id'] = group_id
        
        # Send data to conversion service
        service_result = send_to_conversion_service(processed_data)
        if not service_result['success']:
            return JsonResponse({'error': service_result['error']}, status=service_result['status'])
        
        # Handle conversion service response
        result = handle_conversion_response(service_result['response'], files[0].name)
        if result['success']:
            return result['response']
        elif 'json_response' in result:
            return JsonResponse(result['json_response'], status=result['status'], safe=False)
        else:
            return JsonResponse({'error': result['error']}, status=result['status'])
            
    except Exception as e:
        logger.exception("Unexpected error during conversion")
        return JsonResponse({'error': 'Internal server error'}, status=500)
