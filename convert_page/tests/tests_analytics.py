from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import json
from unittest.mock import patch, MagicMock

class ConvertPageAnalyticsTests(TestCase):
    """Tests for analytics integration in the convert_page view."""
    
    def setUp(self):
        self.client = Client()
        self.csrf_token = self.client.get('/convert_page/').cookies['csrftoken'].value
    
    def test_convert_page_includes_analytics_scripts(self):
        """Test that the convert_page view includes the analytics scripts."""
        response = self.client.get('/convert_page/')
        
        # Verify the response contains the analytics.js script
        self.assertContains(response, '<script src="/static/js/analytics.js"></script>', html=True)
        
        # Verify the response contains the Google Analytics tag
        self.assertContains(response, 'gtag(\'config\', \'G-PD1C44V6LL\')')
    
    @patch('requests.post')
    def test_successful_conversion_tracking(self, mock_post):
        """Test that successful conversions can be tracked."""
        # Create mock ZIP content
        mock_zip_content = b'mock zip content'
        
        # Mock FastAPI response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.content = mock_zip_content
        mock_post.return_value = mock_response
        
        # Create test file
        valid_file = SimpleUploadedFile('file1.class.jet', b'{"valid": "json"}')
        
        # Send POST request with CSRF token and project name
        response = self.client.post(
            '/convert_page/',
            {'files': [valid_file], 'project_name': 'test_project'},
            headers={'X-CSRFToken': self.csrf_token}
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
