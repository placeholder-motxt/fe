from django.test import TestCase, Client
from django.urls import reverse

class LoginSignupTest(TestCase):
    
    def setUp(self):
        """Set up test client and URLs before each test."""
        self.client = Client()
        self.login_url = reverse("login_signup:login")
        self.signup_url = reverse("login_signup:signup")
    
    def test_login_view(self) -> None:
        """Test that login view returns 200 and uses the correct template."""
        response = self.client.get(self.login_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
    
    def test_signup_view(self) -> None:
        """Test that signup view returns 200 and uses the correct template."""
        response = self.client.get(self.signup_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")