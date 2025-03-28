from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.

def login(request: HttpRequest) -> HttpResponse:
    return render(request, "login.html")


def signup(request: HttpRequest) -> HttpResponse:
    return render(request, "signup.html")