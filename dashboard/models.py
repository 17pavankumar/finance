from django.db import models
from django.contrib.auth.models import User

class FinanceMetric(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metrics')
    month = models.CharField(max_length=50) # e.g. "January"
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    expenses = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def profit(self):
        return self.revenue - self.expenses

    def __str__(self):
        return f"{self.user.username} - {self.month}"
