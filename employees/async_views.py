"""
Async views for heavy operations that benefit from concurrency.
These can handle multiple requests simultaneously for better performance.
"""
import asyncio
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from asgiref.sync import sync_to_async
from datetime import timedelta

from .models import Employee, Department
from attendance.models import Attendance, Performance

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
async def async_employee_report(request):
    """
    Generate comprehensive employee report asynchronously.
    This can handle multiple report requests simultaneously.
    """
    try:
        logger.info("Starting async employee report generation")
        
        # Check cache first
        cache_key = 'employee_comprehensive_report'
        cached_report = await sync_to_async(cache.get)(cache_key)
        
        if cached_report:
            logger.info("Returning cached employee report")
            return JsonResponse({
                'success': True,
                'data': cached_report,
                'cached': True,
                'generated_at': cached_report.get('generated_at')
            })
        
        # Generate report asynchronously
        report_data = await generate_employee_report()
        
        # Cache the report for 30 minutes
        await sync_to_async(cache.set)(cache_key, report_data, 1800)
        
        logger.info("Employee report generated successfully")
        return JsonResponse({
            'success': True,
            'data': report_data,
            'cached': False,
            'generated_at': report_data.get('generated_at')
        })
        
    except Exception as e:
        logger.error(f"Error generating employee report: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to generate report',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
async def async_department_analytics(request):
    """
    Generate department analytics asynchronously.
    Processes multiple departments concurrently.
    """
    try:
        logger.info("Starting async department analytics")
        
        # Get all departments
        departments = await sync_to_async(list)(
            Department.objects.all().values('id', 'name')
        )
        
        # Process departments concurrently
        tasks = []
        for dept in departments:
            task = process_department_analytics(dept['id'])
            tasks.append(task)
        
        # Wait for all departments to be processed
        department_analytics = await asyncio.gather(*tasks)
        
        # Combine results
        result = {
            'departments': dict(zip([d['name'] for d in departments], department_analytics)),
            'summary': {
                'total_departments': len(departments),
                'total_employees': sum(d['employee_count'] for d in department_analytics),
                'average_employees_per_dept': sum(d['employee_count'] for d in department_analytics) / len(departments) if departments else 0
            },
            'generated_at': timezone.now().isoformat()
        }
        
        logger.info("Department analytics generated successfully")
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error generating department analytics: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to generate analytics',
            'message': str(e)
        }, status=500)


async def generate_employee_report():
    """
    Generate comprehensive employee report with multiple data sources.
    This function processes different data sources concurrently for better performance.
    
    Returns:
        dict: Complete employee report containing:
            - employee_statistics: Total, active, and inactive employee counts
            - attendance_summary: Attendance status breakdown for last 30 days
            - performance_summary: Performance rating distribution
            - department_distribution: Employee count per department
            - generated_at: Timestamp when report was created
            
    Uses asyncio.gather() to run multiple database queries concurrently,
    significantly improving response time compared to sequential execution.
    """
    # Create concurrent tasks for different data sources
    tasks = [
        get_employee_statistics(),
        get_attendance_summary(),
        get_performance_summary(),
        get_department_distribution()
    ]
    
    # Execute all tasks concurrently
    employee_stats, attendance_summary, performance_summary, dept_distribution = await asyncio.gather(*tasks)
    
    return {
        'employee_statistics': employee_stats,
        'attendance_summary': attendance_summary,
        'performance_summary': performance_summary,
        'department_distribution': dept_distribution,
        'generated_at': timezone.now().isoformat()
    }


async def get_employee_statistics():
    """Get basic employee statistics."""
    total_employees = await sync_to_async(Employee.objects.count)()
    active_employees = await sync_to_async(Employee.objects.filter(is_active=True).count)()
    
    return {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': total_employees - active_employees
    }


async def get_attendance_summary():
    """Get attendance summary for the last 30 days."""
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    attendance_data = await sync_to_async(lambda: list(
        Attendance.objects.filter(date__gte=thirty_days_ago)
        .values('status')
        .annotate(count=models.Count('id'))
    ))()
    
    return {status['status']: status['count'] for status in attendance_data}


async def get_performance_summary():
    """Get performance rating summary."""
    performance_data = await sync_to_async(lambda: list(
        Performance.objects.values('rating')
        .annotate(count=models.Count('id'))
    ))()
    
    return {f"rating_{perf['rating']}": perf['count'] for perf in performance_data}


async def get_department_distribution():
    """Get employee distribution by department."""
    dept_data = await sync_to_async(lambda: list(
        Department.objects.annotate(
            employee_count=models.Count('employees')
        ).values('name', 'employee_count')
    ))()
    
    return {dept['name']: dept['employee_count'] for dept in dept_data}


async def process_department_analytics(department_id):
    """
    Process analytics for a single department.
    This can be run concurrently for multiple departments.
    
    Args:
        department_id (int): The unique ID of the department to analyze
        
    Returns:
        dict: Analytics data containing:
            - department_name: Name of the department
            - employee_count: Number of active employees
            - attendance_count_30_days: Total attendance records in last 30 days
            - attendance_rate_percentage: Calculated attendance rate as percentage
            
    This function calculates the attendance rate by comparing actual attendance
    records against expected attendance (employee_count * 30 days).
    """
    # Get department info
    dept = await sync_to_async(Department.objects.get)(id=department_id)
    
    # Get employee count
    employee_count = await sync_to_async(
        dept.employees.filter(is_active=True).count
    )()
    
    # Get recent attendance for this department
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    attendance_count = await sync_to_async(lambda: 
        Attendance.objects.filter(
            employee__department=dept,
            date__gte=thirty_days_ago
        ).count()
    )()
    
    # Calculate attendance rate
    expected_attendance = employee_count * 30  # 30 days
    attendance_rate = (attendance_count / expected_attendance * 100) if expected_attendance > 0 else 0
    
    return {
        'department_name': dept.name,
        'employee_count': employee_count,
        'attendance_count_30_days': attendance_count,
        'attendance_rate_percentage': round(attendance_rate, 2)
    }


# Health check endpoint for async functionality
@csrf_exempt
@require_http_methods(["GET"])
async def async_health_check(request):
    """
    Health check endpoint that tests async functionality.
    """
    try:
        # Test database connectivity
        employee_count = await sync_to_async(Employee.objects.count)()
        
        # Test cache connectivity
        test_cache_key = 'health_check_test'
        await sync_to_async(cache.set)(test_cache_key, 'test_value', 10)
        cache_value = await sync_to_async(cache.get)(test_cache_key)
        
        return JsonResponse({
            'status': 'healthy',
            'async_working': True,
            'database_accessible': True,
            'cache_accessible': cache_value == 'test_value',
            'employee_count': employee_count,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Async health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)