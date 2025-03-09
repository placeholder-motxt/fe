import io
import os
from unittest.mock import patch, MagicMock
import zipfile
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
import json

from fe import settings

class ConvertPageViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.csrf_token = self.client.get('/convert_page/').cookies['csrftoken'].value

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
        invalid_json = SimpleUploadedFile('test.class.jet', b'{ invalid }')
        response = self.client.post('/convert_page/', {'files': [invalid_json]})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['error'],
            'Invalid JSON content in file: test.class.jet'
        )

    # Corner Test
    def test_post_unicode_decode_error(self):
        invalid_utf8 = SimpleUploadedFile('test.class.jet', b'\x80abc')
        response = self.client.post('/convert_page/', {'files': [invalid_utf8]})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()['error'],
            'Invalid UTF-8 encoding in file: test.class.jet'
        )


    # Positive Test
    @patch('requests.post')
    def test_post_valid_class_file(self, mock_post):
        """POST request with valid .class.jet file returns ZIP containing generated files."""
        # Create mock ZIP content with expected files
        mock_zip_content = io.BytesIO()
        with zipfile.ZipFile(mock_zip_content, 'w') as mock_zip:
            mock_zip.writestr('file1.class.jet_models.py', 'mock_models_content')
            mock_zip.writestr('file1.class.jet_views.py', 'mock_views_content')
        mock_zip_content.seek(0)

        # Mock FastAPI response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = mock_zip_content.read()
        mock_post.return_value = mock_response

        # Read real file from input examples directory
        file_path = os.path.join(settings.BASE_DIR, 'input_examples', 'file1.class.jet')
        with open(file_path, 'rb') as f:
            valid_file = SimpleUploadedFile('file1.class.jet', f.read())

        # Send POST request with CSRF token
        response = self.client.post(
            '/convert_page/',
            {'files': [valid_file]},
            headers={'X-CSRFToken': self.csrf_token}
        )

        # Validate response headers and status
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertIn('attachment; filename="file1.class.jet.zip"', response['Content-Disposition'])

        # Validate ZIP file contents
        zip_content = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_content, 'r') as zip_file:
            self.assertIn('file1.class.jet_models.py', zip_file.namelist())
            self.assertIn('file1.class.jet_views.py', zip_file.namelist())

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
        self.assertEqual(response.status_code, 422)



