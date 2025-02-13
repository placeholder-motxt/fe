from django.test import TestCase, Client
from django.urls import reverse

# Create your tests here.
class LandingPageTest(TestCase):
    
    def test_home(self) -> None:
        c = Client()
        home_url = reverse("landing_page:home")
        
        self.assertEqual(c.get(home_url).status_code, 200)
        self.assertTemplateUsed(c.get(home_url), "landing_page.html")
