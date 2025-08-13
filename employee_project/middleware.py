"""
Custom middleware for rate limiting and request monitoring.
This helps protect your API from being overused or abused.
"""
import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
import time

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """
    Middleware to implement rate limiting across the entire application.
    Think of this as a bouncer at your API's front door.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check rate limit before processing request
        if self.is_rate_limited(request):
            return JsonResponse({
                'error': True,
                'message': 'Rate limit exceeded. Please slow down your requests.',
                'details': 'Too many requests from this IP address.'
            }, status=429)
        
        response = self.get_response(request)
        return response
    
    def is_rate_limited(self, request):
        """
        Check if the current request should be rate limited.
        """
        # Skip rate limiting for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return False
            
        # Get client IP address
        ip = self.get_client_ip(request)
        
        # Different limits for different endpoints
        if request.path.startswith('/api/'):
            return self.check_api_rate_limit(ip, request)
        
        return False
    
    def get_client_ip(self, request):
        """Get the real IP address of the client."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def check_api_rate_limit(self, ip, request):
        """
        Check API-specific rate limits.
        More restrictive for unauthenticated users.
        """
        # Different limits for authenticated vs unauthenticated users
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Authenticated users get higher limits
            limit_key = f'api_rate_limit_user_{request.user.id}'
            max_requests = 200  # per hour
        else:
            # Unauthenticated users get lower limits
            limit_key = f'api_rate_limit_anon_{ip}'
            max_requests = 50   # per hour
        
        # Check current count
        current_count = cache.get(limit_key, 0)
        
        if current_count >= max_requests:
            logger.warning(f'Rate limit exceeded for {ip} - {current_count} requests')
            return True
        
        # Increment counter (expires in 1 hour)
        cache.set(limit_key, current_count + 1, 3600)
        return False