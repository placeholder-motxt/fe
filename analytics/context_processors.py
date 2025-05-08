def google_analytics(request):
    """
    Add Google Analytics tracking ID to the context
    """
    request = request
    return {
        'GA_TRACKING_ID': 'G-PD1C44V6LL'  # Updated tracking ID
    }
