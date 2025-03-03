from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from convert_page.services import JetFileProcessor, FileValidator, JSONParser

class TestJetFileProcessor(TestCase):
    # Positive Test
    def test_process_valid_jet_file(self):
        """Valid .jet file is processed successfully."""
        valid_json = SimpleUploadedFile('test.jet', b'{"key": "value"}')
        processor = JetFileProcessor()
        result = processor.process(valid_json)
        self.assertEqual(result['content'], {"key": "value"})

    # Negative Test
    def test_validate_invalid_extension(self):
        """Validation fails for non-.jet files with consistent error message."""
        invalid_file = SimpleUploadedFile('test.txt', b'{}')
        processor = JetFileProcessor()
        with self.assertRaises(ValueError) as ctx:
            processor.process(invalid_file)  # Validate extension happens during process()
        self.assertEqual(
            str(ctx.exception), 
            'Invalid file type. Only .jet files are allowed'  # Ensure message matches service logic
        )

    # Negative Test
    def test_parse_invalid_json(self):
        """Parsing fails for invalid JSON content with consistent error message."""
        invalid_json = SimpleUploadedFile('test.jet', b'{ invalid }')
        processor = JetFileProcessor()
        with self.assertRaises(ValueError) as ctx:
            processor.process(invalid_json)
        self.assertEqual(
            str(ctx.exception), 
            'Invalid JSON content in the file'  # Ensure message matches service logic
        )

    # Corner Test
    def test_process_unicode_decode_error(self):
        """Processing fails for invalid UTF-8 encoding."""
        invalid_utf8 = SimpleUploadedFile('test.jet', b'\x80abc')
        processor = JetFileProcessor()
        with self.assertRaises(ValueError) as ctx:
            processor.process(invalid_utf8)
        self.assertIn('UnicodeDecodeError', str(ctx.exception))