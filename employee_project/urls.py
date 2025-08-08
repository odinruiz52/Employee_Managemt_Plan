from django.contrib import admin
from django.urls import path, include  # Needed to include app URL files
from rest_framework import permissions  # For Swagger UI permissions
from drf_yasg.views import get_schema_view  # Swagger schema view
from drf_yasg import openapi  # OpenAPI info
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # JWT views


# Swagger Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Employee Management API",
        default_version='v1',
        description="API documentation for Employee Management System",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),  # Django Admin route
    path('api/employees/', include('employees.urls')),  # Employee & Department API endpoints
    path('api/attendance/', include('attendance.urls')),  # Attendance & Performance API endpoints

    # JWT endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # login
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI Docs
]
