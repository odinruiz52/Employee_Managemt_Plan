from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet, PerformanceViewSet

# Set up router for Attendance and Performance
router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet)
router.register(r'performance', PerformanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
