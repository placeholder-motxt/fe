import io
import os
import json
import requests
import zipfile
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile

from fe import settings

class ConvertPageViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.csrf_token = self.client.get('/convert_page/').cookies['csrftoken'].value

    def test_get_request_renders_template(self):
        """GET request returns 200 and renders the correct template."""
        response = self.client.get('/convert_page/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'convert_page.html')

    def test_post_no_file_returns_error(self):
        """POST request without a file returns 400 and an error message."""
        response = self.client.post('/convert_page/', {'project_name': 'test_project'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'No files uploaded')

    def test_post_missing_project_name(self):
        """POST request without a project name returns 400 and an error message."""
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {'files': [valid_file]})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Project name is required')

    def test_post_invalid_project_name_format(self):
        """POST request with invalid project name format returns 400."""
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'invalid-project-name'  # Contains hyphens which are not allowed
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['error'],
            'Project name can only contain letters, numbers, and underscores'
        )

    def test_post_invalid_file_extension(self):
        """POST request with invalid file extension returns 400 and consistent error message."""
        invalid_file = SimpleUploadedFile('test.txt', b'Invalid content')
        response = self.client.post('/convert_page/', {
            'files': [invalid_file],
            'project_name': 'test_project'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['error'],
            'Invalid file type: test.txt'
        )

    def test_post_unicode_decode_error(self):
        """Test handling of files with invalid UTF-8 encoding."""
        invalid_utf8 = SimpleUploadedFile('test.class.jet', b'\x80abc')
        response = self.client.post('/convert_page/', {
            'files': [invalid_utf8],
            'project_name': 'test_project'
        })
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()['error'],
            'Invalid UTF-8 encoding in file: test.class.jet'
        )

    def test_post_duplicate_filenames(self):
        """POST request with duplicate filenames returns 400."""
        file1 = SimpleUploadedFile('file1.class.jet', b'{"key": "value"}')
        file2 = SimpleUploadedFile('file1.class.jet', b'{"key": "value"}')

        response = self.client.post('/convert_page/', {
            'files': [file1, file2],
            'project_name': 'test_project'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Duplicate filenames are not allowed')

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

        # Create test file
        valid_file = SimpleUploadedFile('file1.class.jet', b'{"valid": "json"}')

        # Send POST request with CSRF token and project name
        response = self.client.post(
            '/convert_page/',
            {'files': [valid_file], 'project_name': 'test_project'},
            headers={'X-CSRFToken': self.csrf_token}
        )

        # Validate response headers and status
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertIn('attachment; filename="file1.class.jet.zip"', response['Content-Disposition'])

    @patch('requests.post')
    def test_fastapi_connection_error(self, mock_post):
        """Test FastAPI connection errors (RequestException)"""
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['error'], 'Conversion service unavailable')

    @patch('requests.post')
    def test_invalid_content_type_from_api(self, mock_post):
        """Test handling of invalid content type from FastAPI."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}  # Not zip
        mock_response.content = b'{"result": "success"}'
        mock_post.return_value = mock_response
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()['error'],
            'Invalid response format from conversion service'
        )

    @patch('requests.post')
    def test_api_error_response(self, mock_post):
        """Test handling of error response from FastAPI."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Bad request to API'}
        mock_post.return_value = mock_response
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Bad request to API')

    @patch('requests.post')
    def test_api_error_invalid_json(self, mock_post):
        """Test handling of invalid JSON in error response."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.side_effect = json.JSONDecodeError('Invalid JSON', '', 0)
        mock_post.return_value = mock_response
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['error'], 'Invalid service response')

    @patch('requests.post')
    def test_general_exception(self, mock_post):
        """Test handling of unexpected exceptions."""
        mock_post.side_effect = Exception('Unexpected error')
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['error'], 'Internal server error')

    @patch('requests.post')
    def test_style_theme_passed_to_api(self, mock_post):
        """Test that style theme is correctly passed to the API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project',
            'style-theme': 'vibrant'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Verify the style theme was included in the API call
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        self.assertEqual(json_data['style_theme'], 'vibrant')

    @patch('requests.post')
    def test_default_style_theme(self, mock_post):
        """Test that default style theme is used when none is provided."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Verify the default style theme was included
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        self.assertEqual(json_data['style_theme'], 'modern')

    @patch('requests.post')
    def test_project_type_passed_to_api(self, mock_post):
        """Test that project type is correctly passed to the API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project',
            'project_type': 'spring'
        })
        
        self.assertEqual(response.status_code, 400)
        

    @patch('requests.post')
    def test_default_project_type(self, mock_post):
        """Test that default project type is used when none is provided."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Verify the default project type was included
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        self.assertEqual(json_data['project_type'], 'django')
        
    def test_group_id_required_for_spring(self):
        """Test that group ID is required when project type is spring."""
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project',
            'project_type': 'spring'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['error'],
            'Group ID is required for SpringBoot projects'
        )
        
    def test_invalid_group_id_format(self):
        """Test that group ID is validated to contain at least one dot."""
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project',
            'project_type': 'spring',
            'group_id': 'invalidgroupid'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['error'],
            'Group ID must contain at least one dot (e.g., com.example)'
        )
        
    @patch('requests.post')
    def test_valid_group_id_for_spring(self, mock_post):
        """Test that valid group ID is passed to the API for spring projects."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project',
            'project_type': 'spring',
            'group_id': 'com.example'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Verify the group ID was included in the API call
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        self.assertEqual(json_data['group_id'], 'com.example')
        
    @patch('requests.post')
    def test_valid_sequence_file(self, mock_post):
        """Test processing of .sequence.jet files."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        valid_file = SimpleUploadedFile('valid.sequence.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')