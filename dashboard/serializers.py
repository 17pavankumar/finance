from rest_framework import serializers
from .models import FinanceMetric

class FinanceMetricSerializer(serializers.ModelSerializer):
    profit = serializers.ReadOnlyField()

    class Meta:
        model = FinanceMetric
        fields = ('id', 'month', 'revenue', 'expenses', 'profit', 'created_at')
