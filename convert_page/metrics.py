from prometheus_client import (
    Counter, 
    Histogram, 
)

http_requests_total = Counter(
    'http_requests_101_total', 
    'Total number of HTTP requests received', 
    ['method']  # Labels for request method type
)

REQUEST_LATENCY = Histogram(
    'http_request_latency_seconds', 
    'Histogram of HTTP request durations in seconds',
    ['method']  # You can add labels, such as HTTP method (GET, POST, etc.)
)