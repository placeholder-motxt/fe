from django.urls import path

from convert_page.views import *


app_name = "convert_page"

urlpatterns = [
    path('convert_page/', convert_page, name="convert_page"),
]
