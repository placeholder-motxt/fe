from django.shortcuts import render

def analytics_dashboard(request):
    """
    A simple dashboard view for analytics data
    """
    return render(request, 'analytics/dashboard.html')
