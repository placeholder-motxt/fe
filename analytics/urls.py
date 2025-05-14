from django.urls import path
from analytics.views import analytics_dashboard

urlpatterns = [
    path('', analytics_dashboard, name='analytics_dashboard'),
]
