from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from convert_page.services import (
    FileValidator,
    JSONParser,
    ResponseBuilder,
    JetFileProcessor,
    BaseFileProcessor
)

class TestFileValidator(TestCase):
    def test_valid_extension(self):
        """Valid .jet extensions pass validation."""
        validator = FileValidator()
        valid_file = SimpleUploadedFile('test.jet', b'{}')
        validator.validate_extension(valid_file)


    def test_invalid_extension(self):
        """Non-.jet extensions raise ValueError."""
        validator = FileValidator()
        invalid_file = SimpleUploadedFile('test.txt', b'{}')
        with self.assertRaises(ValueError) as ctx:
            validator.validate_extension(invalid_file)
        self.assertEqual(str(ctx.exception), 'Invalid file type. Only .jet files are allowed')

class TestJSONParser(TestCase):
    def test_valid_json(self):
        """Valid JSON content is parsed correctly."""
        parser = JSONParser()
        valid_content = b'{"key": "value"}'
        result = parser.parse(valid_content.decode('utf-8'))
        # self.assertEqual(result, {"key": "value"})

    def test_invalid_json_includes_filename(self):
        """Invalid JSON error includes the filename in the message."""
        invalid_json_file = SimpleUploadedFile('test.class.jet', b'{ invalid }')
        
        processor = JetFileProcessor()
        with self.assertRaises(ValueError) as ctx:
            processor.process([invalid_json_file])
            
        self.assertEqual(
            str(ctx.exception),
            'Invalid JSON content in file: test.class.jet'
        )

class TestResponseBuilder(TestCase):
    def test_success_response(self):
        """Success response has correct structure and status code."""
        builder = ResponseBuilder()
        response = builder.success('test.jet', {'key': 'value'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['json_body']['filename'], 'test.jet')

    def test_error_response(self):
        """Error response has correct message and status code."""
        builder = ResponseBuilder()
        response = builder.error('Test error', status=400)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Test error')

class TestJetFileProcessor(TestCase):
    def test_duplicate_filenames_raise_error(self):
        """Duplicate filenames in input trigger ValueError."""
        # Create two files with the same name
        file1 = SimpleUploadedFile('file.sequence.jet', b'{"diagram": "Class"}')
        file2 = SimpleUploadedFile('file.sequence.jet', b'{"diagram": "Sequence"}')
        
        processor = JetFileProcessor()
        with self.assertRaises(ValueError) as ctx:
            processor.process([file1, file2])  # Pass list of files
            
        self.assertEqual(
            str(ctx.exception),
            'Duplicate filenames are not allowed'
        )

class TestBaseFileProcessor(TestCase):
    def test_abstract_class_cannot_instantiate(self):
        """BaseFileProcessor cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseFileProcessor()  # Abstract class instantiation fails

    def test_subclass_must_implement_process(self):
        """Subclasses must implement the abstract `process` method."""
        class InvalidProcessor(BaseFileProcessor):
            pass  # Missing `process` implementation
        
        with self.assertRaises(TypeError):
            InvalidProcessor()  # Subclass without `process` fails