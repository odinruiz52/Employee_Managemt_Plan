from django.db import models
from .mixins import BaseModel, TimestampMixin, SoftDeleteMixin

# Department model to store department names
class Department(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, help_text="Optional department description")

    def __str__(self):
        return self.name  # Display department name in admin and queries

# Employee model with personal and department details
class Employee(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    date_of_joining = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Annual salary")
    is_active = models.BooleanField(default=True, help_text="Whether employee is currently active")
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE,
        related_name='employees'  # allows reverse lookup: department.employees.all()
    )

    class Meta:
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['date_of_joining']),
            models.Index(fields=['email']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name  # Display employee name in admin and queries

    @property
    def is_deleted(self):
        """Check if this employee is soft deleted."""
        return self.deleted is not None
