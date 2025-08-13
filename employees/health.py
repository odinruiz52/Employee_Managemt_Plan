"""
Comprehensive health check system for monitoring application status.
This helps ensure your system is running smoothly and alerts you to problems.
"""
import time
import logging
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from io import StringIO

from .models import Employee, Department
from attendance.models import Attendance, Performance

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Comprehensive health check endpoint.
    Returns detailed status of all system components.
    """
    start_time = time.time()
    checks = {}
    overall_status = "healthy"
    
    try:
        # Database connectivity check
        checks['database'] = check_database_health()
        
        # Cache connectivity check
        checks['cache'] = check_cache_health()
        
        # Model accessibility check
        checks['models'] = check_models_health()
        
        # Disk space check (basic)
        checks['system'] = check_system_health()
        
        # Performance check
        checks['performance'] = check_performance_health()
        
        # Determine overall status
        for check_name, check_result in checks.items():
            if not check_result.get('healthy', False):
                overall_status = "unhealthy"
                break
        
        response_time = round((time.time() - start_time) * 1000, 2)  # milliseconds
        
        return JsonResponse({
            'status': overall_status,
            'timestamp': timezone.now().isoformat(),
            'response_time_ms': response_time,
            'checks': checks,
            'version': '1.0.0',  # You can make this dynamic
            'environment': 'development' if settings.DEBUG else 'production'
        }, status=200 if overall_status == "healthy" else 503)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)


def check_database_health():
    """Check database connectivity and basic operations."""
    try:
        start_time = time.time()
        
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Test model access
        employee_count = Employee.objects.count()
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'healthy': True,
            'response_time_ms': response_time,
            'employee_count': employee_count,
            'connection_status': 'connected'
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'healthy': False,
            'error': str(e),
            'connection_status': 'failed'
        }


def check_cache_health():
    """Check cache system connectivity and operations."""
    try:
        start_time = time.time()
        
        # Test cache write/read
        test_key = 'health_check_test'
        test_value = str(timezone.now().timestamp())
        
        cache.set(test_key, test_value, 10)  # 10 seconds
        retrieved_value = cache.get(test_key)
        
        # Clean up
        cache.delete(test_key)
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'healthy': retrieved_value == test_value,
            'response_time_ms': response_time,
            'write_success': True,
            'read_success': retrieved_value == test_value
        }
        
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {
            'healthy': False,
            'error': str(e),
            'write_success': False,
            'read_success': False
        }


def check_models_health():
    """Check that all models are accessible and working."""
    try:
        start_time = time.time()
        
        model_counts = {
            'departments': Department.objects.count(),
            'employees': Employee.objects.count(),
            'attendance_records': Attendance.objects.count(),
            'performance_reviews': Performance.objects.count(),
        }
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'healthy': True,
            'response_time_ms': response_time,
            'model_counts': model_counts,
            'all_accessible': True
        }
        
    except Exception as e:
        logger.error(f"Models health check failed: {e}")
        return {
            'healthy': False,
            'error': str(e),
            'all_accessible': False
        }


def check_system_health():
    """Check basic system health metrics."""
    try:
        import psutil
        
        # Get basic system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'healthy': cpu_percent < 90 and memory.percent < 90 and disk.percent < 90,
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'warnings': [
                w for w in [
                    'High CPU usage' if cpu_percent > 80 else None,
                    'High memory usage' if memory.percent > 80 else None,
                    'Low disk space' if disk.percent > 80 else None,
                ] if w
            ]
        }
        
    except ImportError:
        # psutil not available, do basic check
        return {
            'healthy': True,
            'message': 'System monitoring not available (install psutil for detailed metrics)',
            'basic_check': True
        }
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return {
            'healthy': False,
            'error': str(e)
        }


def check_performance_health():
    """Check application performance metrics."""
    try:
        start_time = time.time()
        
        # Test database query performance
        db_start = time.time()
        recent_attendance = list(Attendance.objects.select_related('employee').order_by('-date')[:10])
        db_time = round((time.time() - db_start) * 1000, 2)
        
        # Test cache performance
        cache_start = time.time()
        cache.set('perf_test', 'test_data', 5)
        cache.get('perf_test')
        cache_time = round((time.time() - cache_start) * 1000, 2)
        
        total_time = round((time.time() - start_time) * 1000, 2)
        
        # Performance thresholds
        db_healthy = db_time < 100  # Less than 100ms
        cache_healthy = cache_time < 10  # Less than 10ms
        
        return {
            'healthy': db_healthy and cache_healthy,
            'total_response_time_ms': total_time,
            'database_query_time_ms': db_time,
            'cache_operation_time_ms': cache_time,
            'performance_grade': 'good' if (db_time < 50 and cache_time < 5) else 'acceptable' if (db_time < 100 and cache_time < 10) else 'slow'
        }
        
    except Exception as e:
        logger.error(f"Performance health check failed: {e}")
        return {
            'healthy': False,
            'error': str(e)
        }


@csrf_exempt
@require_http_methods(["GET"])
def detailed_health_check(request):
    """
    More detailed health check with additional metrics.
    """
    try:
        # Run Django system checks
        output = StringIO()
        call_command('check', stdout=output)
        django_checks = output.getvalue()
        
        # Get recent activity
        recent_employees = Employee.objects.order_by('-created_at')[:5]
        recent_attendance = Attendance.objects.order_by('-created_at')[:5]
        
        # Calculate some basic metrics
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(is_active=True).count()
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'django_checks': 'passed' if 'No issues' in django_checks else 'issues_found',
            'django_check_output': django_checks,
            'metrics': {
                'total_employees': total_employees,
                'active_employees': active_employees,
                'inactive_employees': total_employees - active_employees,
                'recent_activity': {
                    'new_employees_last_5': len(recent_employees),
                    'attendance_records_last_5': len(recent_attendance)
                }
            },
            'database_stats': {
                'total_tables': len(connection.introspection.table_names()),
                'connection_queries': len(connection.queries) if settings.DEBUG else 'N/A (DEBUG=False)'
            }
        })
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check for container orchestration.
    Returns 200 if the application is ready to serve traffic.
    """
    try:
        # Quick checks that the app is ready
        Employee.objects.count()  # Database accessible
        cache.set('readiness_test', 'ready', 1)  # Cache accessible
        
        return JsonResponse({'status': 'ready'})
        
    except Exception as e:
        return JsonResponse({'status': 'not_ready', 'error': str(e)}, status=503)


@csrf_exempt 
@require_http_methods(["GET"])
def liveness_check(request):
    """
    Liveness check for container orchestration.
    Returns 200 if the application is alive (basic Django functionality).
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': timezone.now().isoformat()
    })