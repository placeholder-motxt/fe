import json
from abc import ABC, abstractmethod

from django.http import JsonResponse

class FileValidator:
    def validate_extension(self, file):
        if not file.name.lower().endswith('.jet'):
            raise ValueError('Invalid file type. Only .jet files are allowed')

class JSONParser:
    def parse(self, file_content: str):
        try:
            return json.loads(file_content)
        except json.JSONDecodeError:
            raise ValueError('Invalid JSON content in the file')

class ResponseBuilder:
    def success(self, filename: str, parsed_content: dict) -> JsonResponse:
        return JsonResponse({
            'message': 'File processed successfully',
            'json_body': {
                'filename': filename,
                'content': parsed_content
            }
        })

    def error(self, error_message: str, status: int = 400) -> JsonResponse:
        return JsonResponse({'error': error_message}, status=status)

class BaseFileProcessor(ABC):
    @abstractmethod
    def process(self, file) -> dict:
        pass

class JetFileProcessor:
    def process_multiple(self, files):
        filenames = []
        contents = []

        for file in files:
            # Validate file extension
            if not file.name.lower().endswith(('.class.jet', '.sequence.jet')):
                raise ValueError('Invalid file type. Only .class.jet and .sequence.jet files are allowed')

            # Read and parse file content
            try:
                content = json.loads(file.read().decode('utf-8'))
            except json.JSONDecodeError:
                raise ValueError(f'Invalid JSON content in file: {file.name}')
            except UnicodeDecodeError:
                raise ValueError(f'Invalid UTF-8 encoding in file: {file.name}')

            # Append filename and content
            filenames.append(file.name)
            contents.append([content])  # Wrap content in a list

        # Check for duplicate filenames
        if len(filenames) != len(set(filenames)):
            raise ValueError('Duplicate filenames are not allowed')

        # Check for multiple .class.jet files
        class_files = [name for name in filenames if name.lower().endswith('.class.jet')]
        if len(class_files) > 1:
            raise ValueError('Only one .class.jet file is allowed')

        return {
            'filename': filenames,
            'content': contents
        }