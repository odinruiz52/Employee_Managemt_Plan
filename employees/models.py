from django.db import models
from django.core.validators import EmailValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .mixins import BaseModel, TimestampMixin, SoftDeleteMixin


def validate_salary_range(value):
    """
    Custom validator to ensure salary is within reasonable business limits.
    
    Args:
        value (Decimal): The salary value to validate
        
    Raises:
        ValidationError: If salary is negative or unreasonably high
    """
    if value is not None:
        if value < 0:
            raise ValidationError('Salary cannot be negative.')
        if value > 10000000:  # 10 million cap
            raise ValidationError('Salary cannot exceed $10,000,000.')


def validate_phone_number(value):
    """
    Basic phone number validation to ensure proper format.
    
    Args:
        value (str): Phone number to validate
        
    Raises:
        ValidationError: If phone number format is invalid
    """
    import re
    if value and not re.match(r'^\+?[\d\s\-\(\)]+$', value):
        raise ValidationError('Enter a valid phone number.')
    if value and len(value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')) < 10:
        raise ValidationError('Phone number must be at least 10 digits.')

# Department model to store department names
class Department(BaseModel):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Department name must be unique across organization"
    )
    description = models.TextField(
        blank=True, 
        max_length=500,
        help_text="Optional department description (max 500 characters)"
    )

    def clean(self):
        """Custom validation for the Department model."""
        super().clean()
        if self.name:
            self.name = self.name.strip()  # Remove leading/trailing whitespace
            if len(self.name) < 2:
                raise ValidationError({'name': 'Department name must be at least 2 characters long.'})

    def __str__(self):
        return self.name  # Display department name in admin and queries

# Employee model with personal and department details
class Employee(BaseModel):
    name = models.CharField(
        max_length=100,
        help_text="Full name of the employee"
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Unique email address for the employee"
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[validate_phone_number],
        help_text="Contact phone number (include country code if international)"
    )
    address = models.TextField(
        max_length=500,
        help_text="Full residential address (max 500 characters)"
    )
    date_of_joining = models.DateField(
        help_text="Employee's first day of work"
    )
    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[validate_salary_range],
        help_text="Annual salary in USD"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether employee is currently active"
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE,
        related_name='employees',  # allows reverse lookup: department.employees.all()
        help_text="Department where employee works"
    )

    class Meta:
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['date_of_joining']),
            models.Index(fields=['email']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(salary__isnull=True) | models.Q(salary__gte=0),
                name='positive_salary'
            ),
        ]

    def clean(self):
        """Custom validation for the Employee model."""
        super().clean()
        
        # Validate name
        if self.name:
            self.name = self.name.strip()
            if len(self.name) < 2:
                raise ValidationError({'name': 'Employee name must be at least 2 characters long.'})
        
        # Validate email domain (basic business validation)
        if self.email:
            self.email = self.email.lower().strip()
        
        # Validate date of joining is not in the future
        from django.utils import timezone
        if self.date_of_joining and self.date_of_joining > timezone.now().date():
            raise ValidationError({'date_of_joining': 'Date of joining cannot be in the future.'})

    def __str__(self):
        return self.name  # Display employee name in admin and queries

    @property
    def is_deleted(self):
        """Check if this employee is soft deleted."""
        return self.deleted is not None
