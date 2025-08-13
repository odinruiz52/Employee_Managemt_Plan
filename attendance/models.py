from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from employees.models import Employee
from employees.mixins import BaseModel

# Attendance model to track daily attendance status of employees
class Attendance(BaseModel):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        # Ensure one attendance record per employee per date
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.status}"  # Display attendance summary

# Performance model to store employee performance ratings
class Performance(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating must be between 1 and 5"
    )
    review_date = models.DateField()

    class Meta:
        # Ensure one review per employee per date
        unique_together = ['employee', 'review_date']
        indexes = [
            models.Index(fields=['employee', 'review_date']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.employee.name} - Rating: {self.rating}"  # Display performance summary
