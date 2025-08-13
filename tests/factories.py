"""
Test factories for creating test data.
These are like blueprints for creating fake employees, departments, etc. for testing.
"""
import factory
from django.contrib.auth.models import User
from django.utils import timezone
from employees.models import Department, Employee
from attendance.models import Attendance, Performance


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or 'defaultpassword'
        self.set_password(password)


class DepartmentFactory(factory.django.DjangoModelFactory):
    """Factory for creating test departments."""
    class Meta:
        model = Department
    
    name = factory.Faker('company')


class EmployeeFactory(factory.django.DjangoModelFactory):
    """Factory for creating test employees."""
    class Meta:
        model = Employee
    
    name = factory.Faker('name')
    email = factory.LazyAttribute(lambda obj: f'{obj.name.lower().replace(" ", ".")}@company.com')
    phone_number = factory.Faker('phone_number')
    address = factory.Faker('address')
    date_of_joining = factory.Faker('date_between', start_date='-2y', end_date='today')
    department = factory.SubFactory(DepartmentFactory)


class AttendanceFactory(factory.django.DjangoModelFactory):
    """Factory for creating test attendance records."""
    class Meta:
        model = Attendance
    
    employee = factory.SubFactory(EmployeeFactory)
    date = factory.Faker('date_between', start_date='-30d', end_date='today')
    status = factory.Faker('random_element', elements=['Present', 'Absent', 'Late'])


class PerformanceFactory(factory.django.DjangoModelFactory):
    """Factory for creating test performance reviews."""
    class Meta:
        model = Performance
    
    employee = factory.SubFactory(EmployeeFactory)
    rating = factory.Faker('random_int', min=1, max=5)
    review_date = factory.Faker('date_between', start_date='-1y', end_date='today')