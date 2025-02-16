from django.shortcuts import render

from django.http import HttpRequest, HttpResponse
from django.core import serializers as ser
from django.shortcuts import render

def home(request: HttpRequest) -> HttpResponse:
    return render(request, "repository.html")

def async_move_folder(request: HttpRequest) -> HttpResponse:
    return HttpResponse("200")

def async_create_folder(request: HttpRequest) -> HttpResponse:
    return HttpResponse("200")

def async_delete_folder(request: HttpRequest) -> HttpResponse:
    return HttpResponse("200")

def async_edit_folder(request: HttpRequest) -> HttpResponse:
    return HttpResponse("200")

def async_create_diagram(request: HttpRequest) -> HttpResponse:
    return HttpResponse("200")

def async_delete_diagram(request: HttpRequest) -> HttpResponse:
    return HttpResponse("200")

def async_edit_diagram(request: HttpRequest) -> HttpResponse:
    return HttpResponse("200")