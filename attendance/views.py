from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Attendance, Performance
from .serializers import AttendanceSerializer, PerformanceSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'date', 'employee']
    ordering_fields = ['id', 'date', 'status', 'employee']
    ordering = ['-date']  # newest first

class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating', 'review_date', 'employee']
    ordering_fields = ['id', 'rating', 'review_date', 'employee']
    ordering = ['-review_date']
