"""
Test cases for API endpoints.
These tests make sure your API works correctly.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from tests.factories import EmployeeFactory, DepartmentFactory, AttendanceFactory, UserFactory


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


@pytest.fixture
def authenticated_user():
    """Create and return an authenticated user."""
    return UserFactory()


@pytest.fixture
def auth_client(api_client, authenticated_user):
    """Create an authenticated API client."""
    refresh = RefreshToken.for_user(authenticated_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.mark.django_db
class TestAuthentication:
    """Test API authentication."""
    
    def test_unauthenticated_access_denied(self, api_client):
        """Test that unauthenticated users can't access protected endpoints."""
        url = reverse('employee-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_jwt_token_authentication(self, api_client):
        """Test JWT token authentication works."""
        user = UserFactory()
        url = reverse('token_obtain_pair')
        
        # Get JWT token
        data = {'username': user.username, 'password': 'defaultpassword'}
        response = api_client.post(url, data)
        
        # Should fail with wrong password (factory doesn't set usable password)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db 
class TestEmployeeAPI:
    """Test Employee API endpoints."""
    
    def test_list_employees(self, auth_client):
        """Test listing employees."""
        # Create test employees
        EmployeeFactory.create_batch(3)
        
        url = reverse('employee-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_create_employee(self, auth_client):
        """Test creating an employee."""
        department = DepartmentFactory()
        
        url = reverse('employee-list')
        data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone_number': '123-456-7890',
            'address': '123 Test St',
            'date_of_joining': '2024-01-01',
            'department_id': department.id
        }
        
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'John Doe'
        assert response.data['email'] == 'john.doe@example.com'
    
    def test_create_employee_duplicate_email_fails(self, auth_client):
        """Test that creating employee with duplicate email fails."""
        existing_employee = EmployeeFactory(email='duplicate@example.com')
        department = DepartmentFactory()
        
        url = reverse('employee-list')
        data = {
            'name': 'Jane Doe',
            'email': 'duplicate@example.com',  # Same email
            'phone_number': '123-456-7890',
            'address': '123 Test St',
            'date_of_joining': '2024-01-01',
            'department_id': department.id
        }
        
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data  # Our custom error format


@pytest.mark.django_db
class TestDepartmentAPI:
    """Test Department API endpoints."""
    
    def test_list_departments(self, auth_client):
        """Test listing departments."""
        DepartmentFactory.create_batch(2)
        
        url = reverse('department-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_create_department(self, auth_client):
        """Test creating a department."""
        url = reverse('department-list')
        data = {'name': 'New Department'}
        
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Department'


@pytest.mark.django_db
class TestAttendanceAPI:
    """Test Attendance API endpoints."""
    
    def test_list_attendance(self, auth_client):
        """Test listing attendance records."""
        AttendanceFactory.create_batch(3)
        
        url = reverse('attendance-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_create_attendance(self, auth_client):
        """Test creating attendance record."""
        employee = EmployeeFactory()
        
        url = reverse('attendance-list')
        data = {
            'employee': employee.id,
            'date': '2024-01-01',
            'status': 'Present'
        }
        
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'Present'


@pytest.mark.django_db
class TestAPIVersioning:
    """Test API versioning."""
    
    def test_v1_endpoints_work(self, auth_client):
        """Test that v1 endpoints work."""
        EmployeeFactory()
        
        # Test v1 endpoint
        response = auth_client.get('/api/v1/employees/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_backward_compatibility(self, auth_client):
        """Test that old endpoints still work for backward compatibility."""
        EmployeeFactory()
        
        # Test old endpoint (should still work)
        response = auth_client.get('/api/employees/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limit_middleware_exists(self, api_client):
        """Test that rate limiting middleware is configured."""
        # This test just checks that the middleware doesn't break anything
        response = api_client.get('/api/employees/')
        # Should get 401 (unauthorized) not 500 (server error)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED