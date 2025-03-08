from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
import json

class UserManualPageViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Positive Test
    def test_get_request_renders_template(self):
        """GET request returns 200 and renders the correct template."""
        response = self.client.get('/doc/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_manual.html')