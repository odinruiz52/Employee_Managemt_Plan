# reports/views.py
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json

from employees.models import Department, Employee
from attendance.models import Attendance


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


def dashboard(request):
    """
    Render a page with two charts:
    1) Employees per Department (pie)
    2) Attendance by month, last 12 months (bar)
    """

    # -------- Pie chart: employees per department --------
    # If your Employee.department has related_name='employees', use Count('employees')
    # Otherwise (no related_name), Count('employee') usually works in annotations.
    # If you see "Cannot resolve keyword 'employee'", switch to your actual related_name.
    dept_counts = (
        Department.objects
        .annotate(total=Count('employees'))   # change to 'employees' if you set related_name='employees'
        .order_by('name')
        .values('name', 'total')
    )
    pie_labels = [row['name'] for row in dept_counts]
    pie_data = [row['total'] for row in dept_counts]

    # -------- Bar chart: attendance by month (last 12 months) --------
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
        # choices is list of tuples [(db_value, human_label), ...]
        statuses = [choice[0] for choice in status_field.choices]
    else:
        statuses = ['Present', 'Absent', 'Late']  # adjust if your DB stores different values

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
            # Chart.js will pick colors automatically
        })

    context = {
        "pie_labels_json": json.dumps(pie_labels),
        "pie_data_json": json.dumps(pie_data),
        "bar_labels_json": json.dumps(month_labels),
        "bar_datasets_json": json.dumps(bar_datasets),
    }
    return render(request, "charts.html", context)
