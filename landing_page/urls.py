from django.urls import path

from landing_page.views import home


app_name = "landing_page"

urlpatterns = [
    path('', home, name="home"),
]
