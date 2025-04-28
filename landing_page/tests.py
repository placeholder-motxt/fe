from django.test import TestCase, Client
from django.urls import reverse

class LandingPageTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.home_url = reverse("landing_page:home")
        self.mainpage_url = reverse("landing_page:mainpage")
    
    def test_home(self) -> None:
        """Test that home view works correctly."""
        response = self.client.get(self.home_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "landing_page.html")
    
    def test_mainpage(self) -> None:
        """Test that mainpage view works correctly."""
        response = self.client.get(self.mainpage_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "mainpage.html")