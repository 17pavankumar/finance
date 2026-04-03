from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import FinanceMetric
from .serializers import FinanceMetricSerializer

class FinanceMetricViewSet(viewsets.ModelViewSet):
    serializer_class = FinanceMetricSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FinanceMetric.objects.filter(user=self.request.user).order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
