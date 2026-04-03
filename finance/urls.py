from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinanceRecordViewSet

router = DefaultRouter()
router.register(r'records', FinanceRecordViewSet, basename='record')

urlpatterns = [
    path('', include(router.urls)),
]
