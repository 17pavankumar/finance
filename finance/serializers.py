from rest_framework import serializers
from .models import FinanceRecord

class FinanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceRecord
        fields = '__all__'
        read_only_fields = ('user',)

    def validate_amount(self, value):
        """
        Check that the amount is strictly positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number greater than zero.")
        return value

    def validate(self, data):
        """
        Object-level validation.
        """
        if data.get('type') not in ['income', 'expense']:
            raise serializers.ValidationError({"type": "Invalid type. Must be 'income' or 'expense'."})
        return data
