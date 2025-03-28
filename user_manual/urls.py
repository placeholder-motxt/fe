from django.urls import path

from user_manual.views import show_document


app_name = "landing_page"

urlpatterns = [
    path('', show_document, name="show_document"),
]
