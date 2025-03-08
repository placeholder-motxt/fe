from django.shortcuts import render
from django.http import HttpRequest

# Create your views here.
def show_document(request: HttpRequest):
    return render(request, "user_manual.html")