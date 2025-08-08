from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Attendance, Performance
from .serializers import AttendanceSerializer, PerformanceSerializer

# API viewset for Attendance (CRUD)
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'date', 'employee']  # Filter by employee or date

# API viewset for Performance (CRUD)
class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'date', 'employee']  # Filter by employee or date