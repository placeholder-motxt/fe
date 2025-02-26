from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
import json

class ConvertPageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_request(self):
        """GET request, template bener."""

    def test_post_no_file(self):
        """ POST request, gaada file dan return error."""

    def test_post_invalid_file_extension(self):
        """POST request, invalid file type dan returns error."""

    def test_post_invalid_json_content(self):
        """POST request, invalid JSON content di file .jet."""

    def test_post_valid_file(self):
        """POST request, valid file .jet."""

    def test_post_unicode_decode_error(self):
        """POST request, invalid UTF-8 content di file .jet."""
