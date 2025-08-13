"""
Test cases for all models.
These tests make sure our database models work correctly.
"""
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from tests.factories import EmployeeFactory, DepartmentFactory, AttendanceFactory, PerformanceFactory


@pytest.mark.django_db
class TestDepartmentModel:
    """Test the Department model."""
    
    def test_create_department(self):
        """Test creating a department."""
        department = DepartmentFactory()
        assert department.name
        assert str(department) == department.name
    
    def test_department_can_have_employees(self):
        """Test that departments can have employees."""
        department = DepartmentFactory()
        employee1 = EmployeeFactory(department=department)
        employee2 = EmployeeFactory(department=department)
        
        assert department.employees.count() == 2
        assert employee1 in department.employees.all()
        assert employee2 in department.employees.all()


@pytest.mark.django_db  
class TestEmployeeModel:
    """Test the Employee model."""
    
    def test_create_employee(self):
        """Test creating an employee."""
        employee = EmployeeFactory()
        assert employee.name
        assert employee.email
        assert employee.department
        assert str(employee) == employee.name
    
    def test_employee_email_must_be_unique(self):
        """Test that employee emails must be unique."""
        employee1 = EmployeeFactory(email='test@example.com')
        
        with pytest.raises(IntegrityError):
            EmployeeFactory(email='test@example.com')
    
    def test_employee_belongs_to_department(self):
        """Test that employees belong to departments."""
        department = DepartmentFactory(name='Engineering')
        employee = EmployeeFactory(department=department)
        
        assert employee.department == department
        assert employee in department.employees.all()


@pytest.mark.django_db
class TestAttendanceModel:
    """Test the Attendance model."""
    
    def test_create_attendance(self):
        """Test creating attendance record."""
        attendance = AttendanceFactory()
        assert attendance.employee
        assert attendance.date
        assert attendance.status in ['Present', 'Absent', 'Late']
    
    def test_attendance_unique_per_employee_per_date(self):
        """Test that each employee can only have one attendance per date."""
        employee = EmployeeFactory()
        date = timezone.now().date()
        
        # First attendance should work
        AttendanceFactory(employee=employee, date=date, status='Present')
        
        # Second attendance for same employee and date should fail
        with pytest.raises(IntegrityError):
            AttendanceFactory(employee=employee, date=date, status='Absent')
    
    def test_attendance_string_representation(self):
        """Test the string representation of attendance."""
        attendance = AttendanceFactory(status='Present')
        expected = f"{attendance.employee.name} - {attendance.date} - Present"
        assert str(attendance) == expected


@pytest.mark.django_db
class TestPerformanceModel:
    """Test the Performance model."""
    
    def test_create_performance(self):
        """Test creating performance review."""
        performance = PerformanceFactory()
        assert performance.employee
        assert 1 <= performance.rating <= 5
        assert performance.review_date
    
    def test_performance_rating_validation(self):
        """Test that performance ratings are validated."""
        employee = EmployeeFactory()
        
        # Valid ratings should work
        performance = PerformanceFactory(employee=employee, rating=3)
        performance.full_clean()  # This should not raise an error
        
        # Invalid ratings should fail
        with pytest.raises(ValidationError):
            performance = PerformanceFactory.build(employee=employee, rating=6)
            performance.full_clean()
        
        with pytest.raises(ValidationError):
            performance = PerformanceFactory.build(employee=employee, rating=0)
            performance.full_clean()
    
    def test_performance_unique_per_employee_per_date(self):
        """Test that each employee can only have one review per date."""
        employee = EmployeeFactory()
        date = timezone.now().date()
        
        # First review should work
        PerformanceFactory(employee=employee, review_date=date, rating=4)
        
        # Second review for same employee and date should fail
        with pytest.raises(IntegrityError):
            PerformanceFactory(employee=employee, review_date=date, rating=5)