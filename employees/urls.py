from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, EmployeeViewSet
from .async_views import async_employee_report, async_department_analytics, async_health_check

# Set up router for automatic URL routing
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'employees', EmployeeViewSet)

# Include router URLs plus async endpoints
urlpatterns = [
    path('', include(router.urls)),
    
    # Async endpoints for heavy operations
    path('reports/employees/', async_employee_report, name='async_employee_report'),
    path('analytics/departments/', async_department_analytics, name='async_department_analytics'),
    path('health/', async_health_check, name='async_health_check'),
]
