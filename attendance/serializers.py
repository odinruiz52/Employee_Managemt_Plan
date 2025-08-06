from rest_framework import serializers
from .models import Attendance, Performance

# Serializer for Attendance model
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'  # Include all fields

# Serializer for Performance model
class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = '__all__'
