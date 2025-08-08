from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Attendance, Performance
from .serializers import AttendanceSerializer, PerformanceSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    list: List attendance. Filter by ?employee=, ?date=, ?status=. Order with ?ordering=-date.
    create: Create attendance (JWT required).
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'date', 'employee']
    ordering_fields = ['id', 'date', 'status', 'employee']
    ordering = ['-date']  # newest first

class PerformanceViewSet(viewsets.ModelViewSet):
    """
    list: List performance reviews. Filter by ?employee=, ?rating=, ?review_date=.
    create: Create a review (JWT required).
    """
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating', 'review_date', 'employee']
    ordering_fields = ['id', 'rating', 'review_date', 'employee']
    ordering = ['-review_date']
