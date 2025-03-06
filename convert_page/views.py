import json
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
def convert_page(request: HttpRequest):
    if request.method == 'POST':
        # Get the list of uploaded files
        files = request.FILES.getlist('files')

        # Check if no files were uploaded
        if not files:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        # Check for duplicate filenames
        filenames = [file.name for file in files]
        if len(filenames) != len(set(filenames)):
            return JsonResponse({'error': 'Duplicate filenames are not allowed'}, status=400)

        # Validate and process files
        processed_files = []
        class_files = []

        for file in files:
            # Validate file extension
            if not file.name.lower().endswith(('.class.jet', '.sequence.jet')):
                return JsonResponse({'error': f'Invalid file type: {file.name}'}, status=400)

            # Check for multiple .class.jet files
            if file.name.lower().endswith('.class.jet'):
                class_files.append(file.name)
                if len(class_files) > 1:
                    return JsonResponse({'error': 'Only one .class.jet file is allowed'}, status=400)

            try:
                # Read and parse file content as JSON
                file_content = file.read().decode('utf-8')
                parsed_content = json.loads(file_content)
                processed_files.append([file.name, parsed_content])  # Wrap content in a list
            except json.JSONDecodeError:
                return JsonResponse({'error': f'Invalid JSON content in file: {file.name}'}, status=400)
            except UnicodeDecodeError:
                return JsonResponse({'error': f'Invalid UTF-8 encoding in file: {file.name}'}, status=500)

        print("Processed files:", processed_files)

        # Build the final response
        return JsonResponse({
            'filename': [file[0] for file in processed_files],  # Extract filenames
            'content': [file[1] for file in processed_files]   # Extract contents
        }, status=200)

    # Handle GET requests by rendering the template
    return render(request, "convert_page.html")