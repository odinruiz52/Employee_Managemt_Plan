from django.contrib import admin

from django.contrib import admin
from .models import Department, Employee

admin.site.register(Department)  # simple register
admin.site.register(Employee)
