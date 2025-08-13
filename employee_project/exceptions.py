"""
Custom exception handlers for better API error responses.
This file helps provide clearer error messages to API users.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides more user-friendly error messages.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the error for debugging
        logger.error(f"API Error: {exc} in {context.get('view', 'Unknown view')}")
        
        # Customize the error response format
        custom_response_data = {
            'error': True,
            'message': 'An error occurred',
            'details': response.data
        }
        
        # Handle specific error types with better messages
        if isinstance(exc, IntegrityError):
            if 'unique constraint' in str(exc).lower():
                custom_response_data['message'] = 'This record already exists. Please check for duplicates.'
            else:
                custom_response_data['message'] = 'Database constraint violation.'
        
        response.data = custom_response_data
    
    return response