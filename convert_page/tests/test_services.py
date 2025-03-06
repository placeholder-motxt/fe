from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from convert_page.services import JetFileProcessor

class TestJetFileProcessor(TestCase):
    # Positive Test
    def test_process_valid_jet_file(self):
        """Valid .jet file is processed successfully."""
        valid_json = SimpleUploadedFile('test.class.jet', b'{"key": "value"}')  # Use .class.jet
        processor = JetFileProcessor()

        result = processor.process_multiple([valid_json])

        self.assertEqual(result['filename'], ['test.class.jet'])
        self.assertEqual(result['content'][0][0], {"key": "value"})

    # Negative Test
    def test_validate_invalid_extension(self):
        """Validation fails for non-.jet files with consistent error message."""
        invalid_file = SimpleUploadedFile('test.txt', b'{}')
        processor = JetFileProcessor()
        
        with self.assertRaises(ValueError) as ctx:
            processor.process_multiple([invalid_file])
        
        self.assertEqual(
            str(ctx.exception),
            'Invalid file type. Only .class.jet and .sequence.jet files are allowed'
        )

    # Negative Test
    def test_parse_invalid_json(self):
        """Parsing fails for invalid JSON content with consistent error message."""
        invalid_json = SimpleUploadedFile('test.jet', b'{ invalid }')
        processor = JetFileProcessor()
        
        with self.assertRaises(ValueError) as ctx:
            processor.process_multiple([invalid_json])
        
        self.assertEqual(
            str(ctx.exception),
            'Invalid JSON content in file: test.jet'
        )

    # Corner Test
    def test_process_unicode_decode_error(self):
        """Processing fails for invalid UTF-8 encoding."""
        invalid_utf8 = SimpleUploadedFile('test.jet', b'\x80abc')
        processor = JetFileProcessor()
        
        with self.assertRaises(ValueError) as ctx:
            processor.process_multiple([invalid_utf8])
        
        self.assertIn('UnicodeDecodeError', str(ctx.exception))

    # Positive Test for multiple files
    def test_process_multiple_valid_files(self):
        """Multiple valid files are processed successfully."""
        class_file = SimpleUploadedFile('file1.class.jet', b'{"key": "value"}')
        sequence_file_1 = SimpleUploadedFile('file2.sequence.jet', b'{"key": "value"}')
        sequence_file_2 = SimpleUploadedFile('file3.sequence.jet', b'{"key": "value"}')

        processor = JetFileProcessor()
        result = processor.process_multiple([class_file, sequence_file_1, sequence_file_2])

        self.assertEqual(result['filename'], ['file1.class.jet', 'file2.sequence.jet', 'file3.sequence.jet'])
        self.assertEqual(len(result['content']), 3)  # Ensure all contents are included

    # Negative Test for duplicate filenames
    def test_process_duplicate_filenames(self):
        """Processing fails for duplicate filenames."""
        file1 = SimpleUploadedFile('file1.class.jet', b'{"key": "value"}')
        file2 = SimpleUploadedFile('file1.class.jet', b'{"key": "value"}')

        processor = JetFileProcessor()
        with self.assertRaises(ValueError) as ctx:
            processor.process_multiple([file1, file2])
        self.assertEqual(str(ctx.exception), 'Duplicate filenames are not allowed')

    # Negative Test for multiple .class.jet files
    def test_process_multiple_class_files(self):
        """Processing fails for multiple .class.jet files."""
        class_file_1 = SimpleUploadedFile('file1.class.jet', b'{"key": "value"}')
        class_file_2 = SimpleUploadedFile('file2.class.jet', b'{"key": "value"}')

        processor = JetFileProcessor()
        with self.assertRaises(ValueError) as ctx:
            processor.process_multiple([class_file_1, class_file_2])
        self.assertEqual(str(ctx.exception), 'Only one .class.jet file is allowed')