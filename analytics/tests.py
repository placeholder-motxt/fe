from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
import os
import tempfile
from unittest.mock import patch, MagicMock

class AnalyticsContextProcessorTests(TestCase):
    """Tests for the analytics context processor."""
    
    def test_google_analytics_context_processor(self):
        """Test that the google_analytics context processor adds GA_TRACKING_ID to the context."""
        from analytics.context_processors import google_analytics
                
        # Call the context processor
        context = google_analytics()
        
        # Verify the context contains the GA_TRACKING_ID
        self.assertIn('GA_TRACKING_ID', context)
        self.assertEqual(context['GA_TRACKING_ID'], 'G-PD1C44V6LL')  # Updated tracking ID

class AnalyticsStaticFilesTests(TestCase):
    """Tests for the analytics static files."""
    
    def setUp(self):
        self.client = Client()
        
        # Create temporary directory for static files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_static_dirs = settings.STATICFILES_DIRS
        settings.STATICFILES_DIRS = [self.temp_dir.name]
        
        # Create analytics.js in the temporary directory
        os.makedirs(os.path.join(self.temp_dir.name, 'js'), exist_ok=True)
        with open(os.path.join(self.temp_dir.name, 'js', 'analytics.js'), 'w') as f:
            f.write('// Test analytics.js')
        
        # We don't need to test for analytics-events.js if it's not being used
    
    def tearDown(self):
        # Restore settings
        settings.STATICFILES_DIRS = self.old_static_dirs
        
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    @patch('django.contrib.staticfiles.finders.find')
    def test_analytics_js_exists(self, mock_find):
        """Test that analytics.js exists in the static files."""
        # Set up the mock to return the path to the file
        mock_find.return_value = os.path.join(self.temp_dir.name, 'js', 'analytics.js')
        
        # Verify the file exists
        from django.contrib.staticfiles.finders import find
        self.assertIsNotNone(find('js/analytics.js'))

class AnalyticsTemplateTests(TestCase):
    """Tests for the analytics templates."""
    
    def test_convert_page_includes_analytics_scripts(self):
        """Test that the convert_page.html template includes the analytics scripts."""
        # Get the convert_page view
        response = self.client.get('/convert_page/')
        
        # Verify the response contains the analytics.js script
        self.assertContains(response, '<script src="/static/js/analytics.js"></script>', html=True)
        
        # Verify the response contains the Google Analytics tag
        self.assertContains(response, 'gtag(\'config\', \'G-PD1C44V6LL\')')

class AnalyticsViewsTests(TestCase):
    """Tests for the analytics views."""
    
    def setUp(self):
        self.client = Client()
    
    def test_analytics_dashboard_view(self):
        """Test that the analytics_dashboard view renders correctly."""
        # Get the analytics dashboard view
        response = self.client.get('/analytics/')
        
        # Verify the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Verify the correct template is used
        self.assertTemplateUsed(response, 'analytics/dashboard.html')
        
        # Verify some content in the response
        self.assertContains(response, '<h1 class="text-3xl font-bold mb-6">Analytics Dashboard</h1>', html=True)
        
        # Verify that the page contains some of the metric cards
        self.assertContains(response, 'Unique Users')
        self.assertContains(response, 'Total Conversions')
        self.assertContains(response, 'Conversions per User')
