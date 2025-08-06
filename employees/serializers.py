from rest_framework import serializers
from .models import Department, Employee

# Serializer for Department model
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'  # Include all model fields

# Serializer for Employee model
class EmployeeSerializer(serializers.ModelSerializer):
    # Read department details (nested), but write using department_id
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', write_only=True
    )

    class Meta:
        model = Employee
        fields = [
            'id', 'name', 'email', 'phone_number', 'address',
            'date_of_joining', 'department', 'department_id'
        ]
