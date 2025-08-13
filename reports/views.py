# reports/views.py
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
import json
import logging

from employees.models import Department, Employee
from attendance.models import Attendance

logger = logging.getLogger(__name__)


def _last_12_month_labels():
    """
    Return labels like ['2024-09', ..., '2025-08'], ending in the current month.
    Precise month-walking (no 30/31-day guessing).
    """
    today = timezone.now().date()
    y, m = today.year, today.month

    # Find the month 11 steps ago
    by, bm = y, m
    for _ in range(11):
        if bm == 1:
            by -= 1
            bm = 12
        else:
            bm -= 1

    # Now walk forward collecting 12 labels
    labels = []
    for _ in range(12):
        labels.append(f"{by:04d}-{bm:02d}")
        if bm == 12:
            by += 1
            bm = 1
        else:
            bm += 1

    return labels


def _get_department_employee_counts():
    """
    Get employee counts per department with caching.
    Cache for 15 minutes since department data doesn't change often.
    """
    cache_key = 'department_employee_counts'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        logger.info('Retrieved department counts from cache')
        return cached_data
    
    logger.info('Computing department counts from database')
    dept_counts = (
        Department.objects
        .annotate(total=Count('employees'))
        .order_by('name')
        .values('name', 'total')
    )
    
    pie_labels = [row['name'] for row in dept_counts]
    pie_data = [row['total'] for row in dept_counts]
    
    result = {'labels': pie_labels, 'data': pie_data}
    
    # Cache for 15 minutes (900 seconds)
    cache.set(cache_key, result, 900)
    return result


def _get_attendance_by_month():
    """
    Get attendance data by month with caching.
    Cache for 5 minutes since attendance data updates frequently.
    """
    cache_key = 'attendance_by_month'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        logger.info('Retrieved attendance data from cache')
        return cached_data
    
    logger.info('Computing attendance data from database')
    month_labels = _last_12_month_labels()
    
    # Build an exact start date for the earliest month label (YYYY-MM-01)
    start_label = month_labels[0]
    start_year, start_month = map(int, start_label.split('-'))
    start_date = timezone.datetime(start_year, start_month, 1, tzinfo=timezone.get_current_timezone()).date()

    qs = (
        Attendance.objects
        .filter(date__gte=start_date)
        .annotate(month=TruncMonth('date'))
        .values('month', 'status')
        .order_by('month')
        .annotate(total=Count('id'))
    )

    # Use model choices if available; otherwise fall back to common order
    status_field = Attendance._meta.get_field('status')
    if getattr(status_field, 'choices', None):
        statuses = [choice[0] for choice in status_field.choices]
    else:
        statuses = ['Present', 'Absent', 'Late']

    # Zero-fill every month for every status
    data_by_status = {s: {lbl: 0 for lbl in month_labels} for s in statuses}

    for row in qs:
        m = row['month']  # first day of that month as a date/datetime
        label = f"{m.year:04d}-{m.month:02d}"
        status = row['status']
        total = row['total']
        if status in data_by_status and label in data_by_status[status]:
            data_by_status[status][label] = total

    # Build datasets for Chart.js (stacked bars)
    bar_datasets = []
    for status in statuses:
        bar_datasets.append({
            "label": status,
            "data": [data_by_status[status][lbl] for lbl in month_labels],
        })
    
    result = {'labels': month_labels, 'datasets': bar_datasets}
    
    # Cache for 5 minutes (300 seconds)
    cache.set(cache_key, result, 300)
    return result


@cache_page(60 * 5)  # Cache the entire page for 5 minutes
@vary_on_headers('Authorization')  # Vary cache by user authentication
def dashboard(request):
    """
    Render a page with two charts:
    1) Employees per Department (pie) - cached for 15 minutes
    2) Attendance by month, last 12 months (bar) - cached for 5 minutes
    """
    logger.info('Dashboard view called')
    
    # Get cached data for pie chart
    pie_data = _get_department_employee_counts()
    
    # Get cached data for bar chart  
    bar_data = _get_attendance_by_month()

    context = {
        "pie_labels_json": json.dumps(pie_data['labels']),
        "pie_data_json": json.dumps(pie_data['data']),
        "bar_labels_json": json.dumps(bar_data['labels']),
        "bar_datasets_json": json.dumps(bar_data['datasets']),
    }
    return render(request, "charts.html", context)
