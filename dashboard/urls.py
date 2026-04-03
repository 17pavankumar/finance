from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinanceMetricViewSet

router = DefaultRouter()
router.register(r'metrics', FinanceMetricViewSet, basename='metric')

urlpatterns = [
    path('', include(router.urls)),
]
