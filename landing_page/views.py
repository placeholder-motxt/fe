from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.
def home(request: HttpRequest) -> HttpResponse:
    return render(request, "landing_page.html")

def mainpage(request: HttpRequest) -> HttpResponse:
    return render(request, "mainpage.html")