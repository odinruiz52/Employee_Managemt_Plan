from rest_framework import viewsets, filters  # add filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Department, Employee
from .serializers import DepartmentSerializer, EmployeeSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    # Optional: allow ordering departments by name/id
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['id', 'name']  # fields you can order by
    ordering = ['id']  # default ordering

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['department', 'date_of_joining']  # existing filters
    ordering_fields = ['id', 'name', 'email', 'date_of_joining', 'department']  # allow ?ordering=name
    ordering = ['id']  # default ordering
    