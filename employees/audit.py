"""
Audit logging system for tracking all changes to important data.
This creates a permanent record of who did what and when.
"""
import json
import logging
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger('audit')


class AuditLog(models.Model):
    """
    Model to store audit trail of all important changes.
    Think of this as a detailed security log.
    """
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('VIEW', 'Viewed'),
    ]

    # What happened
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, help_text="Name of the model that was changed")
    object_id = models.CharField(max_length=100, help_text="ID of the object that was changed")
    object_repr = models.CharField(max_length=200, help_text="String representation of the object")
    
    # Who did it
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, help_text="Browser/client information")
    
    # When it happened
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # What changed (stored as JSON)
    changes = models.JSONField(default=dict, help_text="Details of what changed")
    
    # Additional context
    notes = models.TextField(blank=True, help_text="Additional context or notes")

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.action} {self.model_name} by {self.user} at {self.timestamp}"


def log_audit_event(action, instance, user=None, request=None, changes=None, notes=""):
    """
    Helper function to create audit log entries.
    
    Args:
        action: What happened (CREATE, UPDATE, DELETE, etc.)
        instance: The model instance that was affected
        user: Who did it (User object)
        request: HTTP request object (for IP and user agent)
        changes: Dictionary of what changed
        notes: Additional context
    """
    try:
        # Get user info from request if not provided
        if request and not user:
            user = getattr(request, 'user', None)
            if user and not user.is_authenticated:
                user = None
        
        # Get IP and user agent from request
        user_ip = None
        user_agent = ""
        if request:
            user_ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
        
        # Create audit log entry
        audit_entry = AuditLog.objects.create(
            action=action,
            model_name=instance.__class__.__name__,
            object_id=str(instance.pk),
            object_repr=str(instance)[:200],  # Limit length
            user=user,
            user_ip=user_ip,
            user_agent=user_agent,
            changes=changes or {},
            notes=notes
        )
        
        # Also log to file
        logger.info(
            f"AUDIT: {action} {instance.__class__.__name__}({instance.pk}) "
            f"by {user.username if user else 'Anonymous'} "
            f"from {user_ip or 'Unknown IP'}"
        )
        
        return audit_entry
        
    except Exception as e:
        # Don't let audit logging break the main application
        logger.error(f"Failed to create audit log: {e}")
        return None


def get_client_ip(request):
    """Get the real IP address of the client."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Middleware to track user actions
class AuditMiddleware:
    """
    Middleware to automatically track user actions.
    This runs on every request to capture audit information.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request in thread local storage so signal handlers can access it
        import threading
        if not hasattr(threading.current_thread(), 'request'):
            threading.current_thread().request = request
            
        response = self.get_response(request)
        
        # Log significant API actions
        if request.path.startswith('/api/') and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            if hasattr(request, 'user') and request.user.is_authenticated:
                logger.info(
                    f"API {request.method} {request.path} "
                    f"by {request.user.username} "
                    f"from {get_client_ip(request)} "
                    f"- Status: {response.status_code}"
                )
        
        return response


# Signal handlers for automatic audit logging
@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """Automatically log when objects are created or updated."""
    # Only audit specific models
    audited_models = ['Employee', 'Department', 'Attendance', 'Performance']
    
    if sender.__name__ in audited_models:
        import threading
        request = getattr(threading.current_thread(), 'request', None)
        
        action = 'CREATE' if created else 'UPDATE'
        changes = {}
        
        # For updates, try to get the changes
        if not created and hasattr(instance, 'get_dirty_fields'):
            changes = instance.get_dirty_fields()
        
        log_audit_event(
            action=action,
            instance=instance,
            request=request,
            changes=changes,
            notes=f"Auto-logged {action.lower()}"
        )


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    """Automatically log when objects are deleted."""
    audited_models = ['Employee', 'Department', 'Attendance', 'Performance']
    
    if sender.__name__ in audited_models:
        import threading
        request = getattr(threading.current_thread(), 'request', None)
        
        log_audit_event(
            action='DELETE',
            instance=instance,
            request=request,
            notes="Auto-logged deletion"
        )