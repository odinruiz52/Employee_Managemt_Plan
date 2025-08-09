# reports/urls.py
from django.urls import path
from .views import dashboard

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),  # http://127.0.0.1:8000/dashboard/
]
