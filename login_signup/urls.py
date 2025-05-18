from django.urls import path

from login_signup.views import login, signup


app_name = "login_signup"

urlpatterns = [
    path('login/', login, name="login"),
    path('signup/', signup, name="signup"),
]
