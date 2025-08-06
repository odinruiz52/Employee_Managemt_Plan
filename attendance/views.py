from rest_framework import viewsets
from .models import Attendance, Performance
from .serializers import AttendanceSerializer, PerformanceSerializer

# API viewset for Attendance (CRUD)
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

# API viewset for Performance (CRUD)
class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
