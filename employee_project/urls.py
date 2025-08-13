from django.contrib import admin
from django.urls import path, include, re_path  # Needed to include app URL files
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
        contact=openapi.Contact(email="dev@example.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),  # Django Admin route
    
    # Versioned API endpoints
    path('api/v1/employees/', include('employees.urls')),  # Employee & Department API endpoints v1
    path('api/v1/attendance/', include('attendance.urls')),  # Attendance & Performance API endpoints v1
    
    # Backward compatibility (redirect to v1)
    path('api/employees/', include('employees.urls')),  # Backward compatible
    path('api/attendance/', include('attendance.urls')),  # Backward compatible

    # JWT endpoints (versioned)
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair_v1'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_v1'),
    
    # Backward compatible auth endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Swagger & Redoc (versioned)
    re_path(r'^api/v1/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json-v1'),
    path('api/v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-v1'),
    path('api/v1/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),
    
    # Backward compatible docs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Reports (charts)
    path('', include('reports.urls')),  # adds /dashboard/
]
