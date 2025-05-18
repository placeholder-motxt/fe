from django.shortcuts import render
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def analytics_dashboard(request):
    """
    A simple dashboard view for analytics data
    """
    return render(request, 'analytics/dashboard.html')
