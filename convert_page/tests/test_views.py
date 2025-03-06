from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
import json

class ConvertPageViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    # Positive Test
    def test_get_request_renders_template(self):
        """GET request returns 200 and renders the correct template."""
        response = self.client.get('/convert_page/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'convert_page.html')

    # Negative Test
    def test_post_no_file_returns_error(self):
        """POST request without a file returns 400 and an error message."""
        response = self.client.post('/convert_page/', {'files': []})  # Pass an empty list for 'files'
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'No file uploaded')

    # Negative Test
    def test_post_invalid_file_extension(self):
        """POST request with invalid file extension returns 400 and consistent error message."""
        invalid_file = SimpleUploadedFile('test.txt', b'Invalid content')
        response = self.client.post('/convert_page/', {'files': [invalid_file]})  # Use 'files' key
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['error'],
            'Invalid file type. Only .class.jet and .sequence.jet files are allowed'
        )

    # Negative Test
    def test_post_invalid_json_content(self):
        """POST request with invalid JSON content returns 400 and consistent error message."""
        invalid_json = SimpleUploadedFile('test.jet', b'{ invalid json }')
        response = self.client.post('/convert_page/', {'files': [invalid_json]})  # Use 'files' key
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['error'],
            'Invalid JSON content in file: test.jet'
        )

    # Corner Test
    def test_post_unicode_decode_error(self):
        """POST request with invalid UTF-8 content returns 500."""
        invalid_utf8_content = b'\x80abc'  # Invalid UTF-8 byte sequence
        invalid_file = SimpleUploadedFile('test.jet', invalid_utf8_content)
        response = self.client.post('/convert_page/', {'files': [invalid_file]})  # Use 'files' key
        self.assertEqual(response.status_code, 500)

    # Positive Test
    def test_post_valid_file(self):
        """POST request with valid .jet file returns 200 and correct JSON structure."""
        valid_json_content = json.dumps({
            "diagram": "ClassDiagram",
            "nodes": [{"name": "TestNode"}],
            "version": "3.8"
        }).encode('utf-8')
        valid_file = SimpleUploadedFile('test.class.jet', valid_json_content)

        response = self.client.post('/convert_page/', {'files': [valid_file]})  # Use 'files' key
        print(response.json())
        self.assertEqual(response.status_code, 200)  # Expect 200 OK

        data = response.json()
        self.assertEqual(data['filename'], ['test.class.jet'])  # Expect a list of filenames
        self.assertEqual(len(data['content']), 1)  # Expect one content entry
        self.assertEqual(data['content'][0]['diagram'], 'ClassDiagram')  # Validate nested content
        self.assertEqual(data['content'][0]['version'], '3.8')  # Validate version
        self.assertEqual(data['content'][0]['nodes'][0]['name'], 'TestNode')  # Validate nodes

    # Positive Test for multiple files
    def test_post_multiple_valid_files(self):
        """POST request with multiple valid files returns 200 and correct JSON structure."""
        class_file = SimpleUploadedFile('file1.class.jet', b'{"key": "value"}')
        sequence_file_1 = SimpleUploadedFile('file2.sequence.jet', b'{"key": "value"}')
        sequence_file_2 = SimpleUploadedFile('file3.sequence.jet', b'{"key": "value"}')

        response = self.client.post('/convert_page/', {
            'files': [class_file, sequence_file_1, sequence_file_2]
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['filename'], ['file1.class.jet', 'file2.sequence.jet', 'file3.sequence.jet'])
        self.assertEqual(len(data['content']), 3)  # Ensure all contents are included

    # Negative Test for duplicate filenames
    def test_post_duplicate_filenames(self):
        """POST request with duplicate filenames returns 400."""
        file1 = SimpleUploadedFile('file1.class.jet', b'{"key": "value"}')
        file2 = SimpleUploadedFile('file1.class.jet', b'{"key": "value"}')

        response = self.client.post('/convert_page/', {
            'files': [file1, file2]
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Duplicate filenames are not allowed')

    # Negative Test for multiple .class.jet files
    def test_post_multiple_class_files(self):
        """POST request with multiple .class.jet files returns 400."""
        class_file_1 = SimpleUploadedFile('file1.class.jet', b'{"key": "value"}')
        class_file_2 = SimpleUploadedFile('file2.class.jet', b'{"key": "value"}')

        response = self.client.post('/convert_page/', {
            'files': [class_file_1, class_file_2]
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Only one .class.jet file is allowed')