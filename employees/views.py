from rest_framework import viewsets, filters  # add filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Department, Employee
from .serializers import DepartmentSerializer, EmployeeSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Add filtering and ordering capabilities
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['id', 'name']  # fields you can order by
    ordering = ['id']  # default ordering

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    list: List employees (paginated). Supports ?department=, ?date_of_joining=, ?ordering=.
    create: Create an employee (JWT required). Provide name, email, phone, address, date_of_joining, department_id.
    retrieve: Get one employee by id.
    update: Replace an employee (JWT required).
    partial_update: Update some fields (JWT required).
    destroy: Delete an employee (JWT required).
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Add filtering and ordering capabilities
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['department', 'date_of_joining']  # existing filters
    ordering_fields = ['id', 'name', 'email', 'date_of_joining', 'department']  # allow ?ordering=name
    ordering = ['id']  # default ordering
    