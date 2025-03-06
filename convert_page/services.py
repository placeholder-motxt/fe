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

class JetFileProcessor(BaseFileProcessor):
    def __init__(self):
        self.validator = FileValidator()
        self.parser = JSONParser()

    def process(self, file):
        try:
            self.validator.validate_extension(file)
            content = file.read().decode('utf-8')
            return self.parser.parse(content)
        except ValueError as e:
            # Ensure these messages match the tests
            if "Invalid file type" in str(e):
                raise ValueError('Invalid file type. Only .jet files are allowed')
            elif "Invalid JSON" in str(e):
                raise ValueError('Invalid JSON content in the file')
            else:
                raise e