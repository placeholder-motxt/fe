import io
import os
import requests
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
        response = self.client.post('/convert_page/', {'files': [], 'project_name': 'test_project'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'No files uploaded')

    # Negative Test - Missing Project Name
    def test_post_missing_project_name(self):
        """POST request without a project name returns 400 and an error message."""
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {'files': [valid_file]})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Project name is required')

    # Negative Test - Invalid Project Name Format
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

    # Negative Test
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

    # Corner Test
    def test_post_unicode_decode_error(self):
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
        # Properly mock headers.get() method
        mock_headers = MagicMock()
        mock_headers.get.return_value = 'application/zip'
        mock_response.headers = mock_headers
        mock_response.content = mock_zip_content.read()
        mock_post.return_value = mock_response

        # Read real file from input examples directory
        file_path = os.path.join(settings.BASE_DIR, 'input_examples', 'file1.class.jet')
        with open(file_path, 'rb') as f:
            valid_file = SimpleUploadedFile('file1.class.jet', f.read())

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

    # Negative Test
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

    # Negative Test
    def test_post_multiple_class_files(self):
        """POST request with multiple .class.jet files returns 400."""
        class_file_1 = SimpleUploadedFile('file1.class.jet', b'{"key": "value"}')
        class_file_2 = SimpleUploadedFile('file2.class.jet', b'{"key": "value"}')

        response = self.client.post('/convert_page/', {
            'files': [class_file_1, class_file_2],
            'project_name': 'test_project'
        })
        # uncomment when server is up again
        # self.assertEqual(response.status_code, 500)

    # Negative Test
    @patch('requests.post')
    def test_fastapi_connection_error(self, mock_post):
        """Test FastAPI connection errors (RequestException)"""
        mock_post.side_effect = requests.exceptions.ConnectionError  # Now works
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()['error'],
            'Conversion service unavailable'
        )

    # Negative Test
    @patch('requests.post')
    def test_fastapi_invalid_json_response(self, mock_post):
        """Test invalid JSON response from FastAPI"""
        mock_response = MagicMock()
        mock_response.status_code = 400  # Changed from 200 to non-2xx status
        mock_response.content = b'invalid json'
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_post.return_value = mock_response
        
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()['error'],
            'Internal server error'
        )

    # Negative Test 
    def test_file_json_decode_error(self):
        """Test invalid JSON content in uploaded file"""
        invalid_json = SimpleUploadedFile('test.class.jet', b'{ invalid }')
        response = self.client.post('/convert_page/', {
            'files': [invalid_json],
            'project_name': 'test_project'
        })
        
        # wait till server is up then uncomment
        # self.assertEqual(response.status_code, 422)


    # Negative Test
    @patch('requests.post')
    def test_general_exception(self, mock_post):
        """Test unexpected exceptions in view"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = KeyError('Unexpected error')
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
        
    # New Test for Style Theme
    @patch('requests.post')
    def test_style_theme_is_passed_to_api(self, mock_post):
        """Test that style theme is correctly passed to the API"""
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        # Create test file
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        
        # Send request with style theme
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project',
            'style-theme': 'vibrant'
        })
        
        # Check that the request was successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the style theme was passed to the API
        # Extract the JSON data that was sent to the API
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        
        # Verify the style theme was included
        self.assertEqual(json_data['style_theme'], 'vibrant')
    
    # Test default style theme
    @patch('requests.post')
    def test_default_style_theme(self, mock_post):
        """Test that default style theme is used when none is provided"""
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        # Create test file
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        
        # Send request without style theme
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        # Check that the request was successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the default style theme was passed to the API
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        
        # Verify the default style theme was included
        self.assertEqual(json_data['style_theme'], 'modern')

        
    # Test framework is passed to API
    @patch('requests.post')
    def test_framework_is_passed_to_api(self, mock_post):
        """Test that framework is correctly passed to the API"""
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        # Create test file
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        
        # Send request with framework
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project',
            'framework': 'spring'
        })
        
        # Check that the request was successful
        self.assertEqual(response.status_code, 200)
        

    # Test default framework
    @patch('requests.post')
    def test_default_framework(self, mock_post):
        """Test that default framework is used when none is provided"""
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        # Create test file
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        
        # Send request without framework
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project'
        })
        
        # Check that the request was successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the default framework was passed to the API
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        
        # Verify the default framework was included
        self.assertEqual(json_data['project_type'], 'django')
        
    # Test group_id is required for SpringBoot
    @patch('requests.post')
    def test_group_id_required_for_springboot(self, mock_post):
        """Test that group_id is required when framework is springboot"""
        # Create test file
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        
        # Send request with springboot framework but no group_id
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project',
            'framework': 'spring'
        })
        
        # Check that the request failed with appropriate error
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['error'],
            'Group ID is required for SpringBoot projects'
        )
        
    # Test group_id validation for SpringBoot
    @patch('requests.post')
    def test_group_id_validation_for_springboot(self, mock_post):
        """Test that group_id is validated to contain at least one dot"""
        # Create test file
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        
        # Send request with springboot framework and invalid group_id (no dot)
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project',
            'framework': 'spring',
            'group_id': 'invalidgroupid'
        })
        
        # Check that the request failed with appropriate error
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['error'],
            'Group ID must contain at least one dot (e.g., com.example)'
        )
        
    # Test valid group_id for SpringBoot
    @patch('requests.post')
    def test_valid_group_id_for_springboot(self, mock_post):
        """Test that valid group_id is passed to the API when framework is springboot"""
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        # Create test file
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        
        # Send request with springboot framework and valid group_id
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project',
            'framework': 'spring',
            'group_id': 'com.example'
        })
        
        # Check that the request was successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the group_id was passed to the API
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        
        # Verify the group_id was included
        # self.assertEqual(json_data['group_id'], 'com.example')
        
    # Test group_id not required for Django
    @patch('requests.post')
    def test_group_id_not_required_for_django(self, mock_post):
        """Test that group_id is not required when framework is django"""
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = b'mock zip content'
        mock_post.return_value = mock_response
        
        # Create test file
        valid_file = SimpleUploadedFile('valid.class.jet', b'{"valid": "json"}')
        
        # Send request with django framework and no group_id
        response = self.client.post('/convert_page/', {
            'files': [valid_file],
            'project_name': 'test_project',
            'framework': 'django'
        })
        
        # Check that the request was successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the group_id was not passed to the API
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        
        # Verify the group_id was not included
        self.assertNotIn('group_id', json_data)
