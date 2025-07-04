"""
URL configuration for fe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django_prometheus import exports
from django.http import HttpResponseNotFound
from django.shortcuts import render

def page_404(request):
    return HttpResponseNotFound(render(request, '404.html'))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("landing_page.urls")),
    path('', include("login_signup.urls")),
    path('', include("convert_page.urls")),
    path('doc/', include('user_manual.urls')),
    path('analytics/', include('analytics.urls')),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    path("metrics/", exports.ExportToDjangoView, name="metrics"),
    path('404/', page_404),
]
