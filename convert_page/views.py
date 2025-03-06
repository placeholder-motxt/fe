from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from convert_page.services import JetFileProcessor, ResponseBuilder

@csrf_exempt
def convert_page(request: HttpRequest):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return ResponseBuilder().error('No file uploaded', status=400)

        uploaded_file = request.FILES['file']
        processor = JetFileProcessor()

        try:
            parsed_content = processor.process(uploaded_file)
            return ResponseBuilder().success(uploaded_file.name, parsed_content)
        except ValueError as e:  # error validasi 400
            return ResponseBuilder().error(str(e), status=400)
        except Exception as e:  # Error unexpected 500
            return ResponseBuilder().error(str(e), status=500)
    
    return render(request, "convert_page.html")