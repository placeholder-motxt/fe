import json
from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse

class FileValidator:
    def validate_extension(self, file: UploadedFile):
        """Validate .class.jet and .sequence.jet extensions."""
        if not file.name.lower().endswith(('.class.jet', '.sequence.jet')):
            raise ValueError(f'Invalid file type: {file.name}. Only .class.jet and .sequence.jet allowed')

class JSONParser:
    def parse(self, file_content) -> dict:
        """Parse JSON content from file bytes or string."""
        try:
            # Handle both bytes and string input
            if isinstance(file_content, bytes):
                return json.loads(file_content.decode('utf-8'))
            return json.loads(file_content)
        except json.JSONDecodeError as e:
            raise ValueError('Invalid JSON content in file') from e
        except UnicodeDecodeError as e:
            raise ValueError('Invalid UTF-8 encoding in file') from e

class ResponseBuilder:
    def success(self, filename: str, parsed_content: list) -> JsonResponse:
        """Build success response for valid files."""
        return JsonResponse({
            'message': 'Files processed successfully',
            "json_body": {
                "filename": filename,
                "content": parsed_content
            }
        })

    def error(self, error_message: str, status: int = 400) -> JsonResponse:
        """Build error response."""
        return JsonResponse({'error': error_message}, status=status)

class JetFileProcessor:
    def process(self, files: list[UploadedFile]) -> dict:
        """Process multiple .jet files with validation."""
        validator = FileValidator()
        parser = JSONParser()
        filenames = [file.name for file in files]

        # Validate duplicates
        if len(filenames) != len(set(filenames)):
            raise ValueError('Duplicate filenames are not allowed')

        # Validate only one .class.jet file
        class_files = [name for name in filenames if name.lower().endswith('.class.jet')]
        if len(class_files) > 1:
            raise ValueError('Only one .class.jet file is allowed')

        processed_data = {
            "filename": filenames,
            "content": []
        }

        for file in files:
            validator.validate_extension(file)  # Validate extension first
            content = parser.parse(file.read())  # Parse JSON/UTF-8
            processed_data['content'].append([content])  # Match FastAPI's input format

        return processed_data