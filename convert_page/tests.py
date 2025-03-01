from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
import json

class ConvertPageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_request(self):
        """GET request, template bener."""
        response = self.client.get('/convert_page/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'convert_page.html')

    def test_post_no_file(self):
        """ POST request, gaada file dan return error."""
        response = self.client.post('/convert_page/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'No file uploaded')

    def test_post_invalid_file_extension(self):
        """POST request, invalid file type dan returns error."""
        invalid_file = SimpleUploadedFile('test.txt', b'Invalid content')
        response = self.client.post('/convert_page/', {'file': invalid_file})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid file type. Only .jet files are allowed')

    def test_post_invalid_json_content(self):
        """POST request, invalid JSON content di file .jet."""
        invalid_json = SimpleUploadedFile('test.jet', b'{ invalid json }')
        response = self.client.post('/convert_page/', {'file': invalid_json})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid JSON content in the file')

    def test_post_valid_file(self):
        """POST request, valid file .jet."""
        # Create a valid JSON content
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

    def test_post_unicode_decode_error(self):
        """POST request, invalid UTF-8 content di file .jet."""
        invalid_utf8_content = b'\x80abc'  # Invalid UTF-8 byte sequence
        invalid_file = SimpleUploadedFile('test.jet', invalid_utf8_content)
        
        response = self.client.post('/convert_page/', {'file': invalid_file})
        self.assertEqual(response.status_code, 500)
        self.assertIn('UnicodeDecodeError', response.json()['error'])
