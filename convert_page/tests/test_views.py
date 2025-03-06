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
        response = self.client.post('/convert_page/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'No file uploaded')

    # Negative Test
    def test_post_invalid_file_extension(self):
        """POST request dengan ekstensi salah mengembalikan 400 dan pesan error yang konsisten."""
        invalid_file = SimpleUploadedFile('test.txt', b'Invalid content')
        response = self.client.post('/convert_page/', {'file': invalid_file})
        self.assertEqual(response.status_code, 400)  # Pastikan status 400
        self.assertEqual(
            'Invalid file type. Only .jet files are allowed'  # Sesuai dengan service
        )

    # Negative Test
    def test_post_invalid_json_content(self):
        """POST request dengan konten JSON invalid mengembalikan 400 dan pesan error yang konsisten."""
        invalid_json = SimpleUploadedFile('test.jet', b'{ invalid json }')
        response = self.client.post('/convert_page/', {'file': invalid_json})
        self.assertEqual(response.status_code, 400)  # Pastikan status 400
        self.assertEqual(
            'Invalid JSON content in the file'  # Sesuai dengan service
        )

    # Corner Test
    def test_post_unicode_decode_error(self):
        """POST request with invalid UTF-8 content returns 500."""
        invalid_utf8_content = b'\x80abc'  # Invalid UTF-8 byte sequence
        invalid_file = SimpleUploadedFile('test.jet', invalid_utf8_content)
        response = self.client.post('/convert_page/', {'file': invalid_file})
        self.assertEqual(response.status_code, 500)

    # Positive Test
    def test_post_valid_file(self):
        """POST request with valid .jet file returns 200 and correct JSON structure."""
        valid_json_content = json.dumps({
            "diagram": "ClassDiagram",
            "nodes": [{"name": "TestNode"}],
            "version": "3.8"
        }).encode('utf-8')
        valid_file = SimpleUploadedFile('test.jet', valid_json_content)
        
        response = self.client.post('/convert_page/', {'file': valid_file})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['message'], 'File processed successfully')
        self.assertEqual(data['json_body']['filename'], 'test.jet')
        self.assertIn('content', data['json_body'])