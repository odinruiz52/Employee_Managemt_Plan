from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, EmployeeViewSet

# Set up router for automatic URL routing
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'employees', EmployeeViewSet)

# Include router URLs
urlpatterns = [
    path('', include(router.urls)),
]
