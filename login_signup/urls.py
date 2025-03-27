from django.urls import path

from login_signup.views import *


app_name = "landing_page"

urlpatterns = [
    path('login/', login, name="login"),
    path('signup/', signup, name="signup"),
]
