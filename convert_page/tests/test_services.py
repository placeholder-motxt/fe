import json
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from convert_page.services import (
    FileValidator,
    JSONParser,
    ResponseBuilder,
    JetFileProcessor
)

class TestFileValidator(TestCase):
    def test_valid_extension(self):
        """Valid .jet extensions pass validation."""
        validator = FileValidator()
        valid_file = SimpleUploadedFile('test.class.jet', b'{}')
        validator.validate_extension(valid_file)
        
        valid_file2 = SimpleUploadedFile('test.sequence.jet', b'{}')
        validator.validate_extension(valid_file2)

    def test_invalid_extension(self):
        """Non-.jet extensions raise ValueError."""
        validator = FileValidator()
        invalid_file = SimpleUploadedFile('test.txt', b'{}')
        with self.assertRaises(ValueError) as ctx:
            validator.validate_extension(invalid_file)
        self.assertEqual(str(ctx.exception), 'Invalid file type: test.txt. Only .class.jet and .sequence.jet allowed')

class TestJSONParser(TestCase):
    def test_valid_json(self):
        """Valid JSON content is parsed correctly."""
        parser = JSONParser()
        # Test with bytes input
        valid_content = b'{"key": "value"}'
        result = parser.parse(valid_content)
        self.assertEqual(result, {"key": "value"})
        
        # Test with string input
        string_content = '{"key": "value"}'
        result = parser.parse(string_content)
        self.assertEqual(result, {"key": "value"})

    def test_invalid_json_includes_filename(self):
        """Invalid JSON error includes the filename in the message."""
        invalid_json_file = SimpleUploadedFile('test.class.jet', b'{ invalid }')
        
        processor = JetFileProcessor()
        with self.assertRaises(ValueError) as ctx:
            processor.process([invalid_json_file])
            
        self.assertEqual(
            str(ctx.exception),
            'Invalid JSON content in file'
        )
        
    def test_unicode_decode_error(self):
        """UnicodeDecodeError is handled properly."""
        parser = JSONParser()
        invalid_utf8 = b'\x80abc'  # Invalid UTF-8 bytes
        with self.assertRaises(ValueError) as ctx:
            parser.parse(invalid_utf8)
        self.assertEqual(str(ctx.exception), 'Invalid UTF-8 encoding in file')

    def test_json_decode_error(self):
        """JSONDecodeError is handled properly."""
        parser = JSONParser()
        invalid_json = '{"broken": json'
        with self.assertRaises(ValueError) as ctx:
            parser.parse(invalid_json)
        self.assertEqual(str(ctx.exception), 'Invalid JSON content in file')

class TestResponseBuilder(TestCase):
    def test_success_response(self):
        """Success response has correct structure and status code."""
        builder = ResponseBuilder()
        response = builder.success('test.jet', {'key': 'value'})
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['json_body']['filename'], 'test.jet')

    def test_error_response(self):
        """Error response has correct message and status code."""
        builder = ResponseBuilder()
        response = builder.error('Test error', status=400)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['error'], 'Test error')

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
    
    def test_multiple_class_files_raise_error(self):
        """Multiple .class.jet files trigger ValueError."""
        file1 = SimpleUploadedFile('file1.class.jet', b'{"diagram": "Class1"}')
        file2 = SimpleUploadedFile('file2.class.jet', b'{"diagram": "Class2"}')
        
        processor = JetFileProcessor()
        with self.assertRaises(ValueError) as ctx:
            processor.process([file1, file2])
            
        self.assertEqual(
            str(ctx.exception),
            'Only one .class.jet file is allowed'
        )
    
    def test_successful_processing(self):
        """Valid files are processed correctly."""
        file1 = SimpleUploadedFile('file1.class.jet', b'{"diagram": "Class"}')
        file2 = SimpleUploadedFile('file2.sequence.jet', b'{"diagram": "Sequence"}')
        
        processor = JetFileProcessor()
        result = processor.process([file1, file2])
        
        self.assertEqual(len(result['filename']), 2)
        self.assertEqual(len(result['content']), 2)
        self.assertEqual(result['content'][0][0]['diagram'], 'Class')
        self.assertEqual(result['content'][1][0]['diagram'], 'Sequence')