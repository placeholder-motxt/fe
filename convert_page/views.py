from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json

@csrf_exempt  # Disable CSRF protection for simplicity (use proper CSRF handling in production)
def convert_page(request: HttpRequest):
    if request.method == 'POST':
        # Check if a file was uploaded

        # csrf_token = request.COOKIES.get('csrftoken')  # Retrieve CSRF token from cookies
        # if not csrf_token or csrf_token != request.session.get('csrf_token'):
        #     return JsonResponse({'error': 'CSRF token validation failed'}, status=403)

        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        uploaded_file = request.FILES['file']

        # Validate the file extension
        if not uploaded_file.name.lower().endswith('.jet'):
            return JsonResponse({'error': 'Invalid file type. Only .jet files are allowed'}, status=400)

        try:
            # Read the content of the file
            file_content = uploaded_file.read().decode('utf-8')  # Assuming the file contains JSON data

            # Parse the JSON content
            try:
                parsed_content = json.loads(file_content)  # Parse the JSON string into a Python dictionary
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON content in the file'}, status=400)

            # Construct the JSON body that would have been sent to the backend API
            json_body = {
                'filename': uploaded_file.name,
                'content': parsed_content  # The parsed JSON content from the file
            }

            # Return the JSON body as part of the response
            return JsonResponse({
                'message': 'File processed successfully',
                'json_body': json_body
            })

        except Exception as e:
            # Handle any errors during file processing
            return JsonResponse({'error': str(e)}, status=500)

    # Render the HTML page for GET requests
    return render(request, "convert_page.html")