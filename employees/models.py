from django.db import models

# Department model to store department names
class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name  # Display department name in admin and queries

# Employee model with personal and department details
class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    date_of_joining = models.DateField()
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
        ]

    def __str__(self):
        return self.name  # Display employee name in admin and queries
