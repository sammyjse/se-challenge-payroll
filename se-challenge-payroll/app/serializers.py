from rest_framework import serializers
from .models import Timekeeping, Reports

"""
Serializers for the Timekeeping, and Reports models.

"""


class TimekeepingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timekeeping
        fields = '__all__'


class ReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reports
        fields = '__all__'
