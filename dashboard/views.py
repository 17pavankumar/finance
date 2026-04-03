from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from finance.models import FinanceRecord
from users.permissions import IsViewer

class DashboardDataViewSet(viewsets.ViewSet):
    permission_classes = [IsViewer]

    def _get_base_queryset(self, request):
        role = request.user.profile.role
        if role == 'admin':
            return FinanceRecord.objects.all()
        return FinanceRecord.objects.filter(user=request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        # Step 1: Get all records based on user role (Admin sees all, Viewer sees their own)
        qs = self._get_base_queryset(request)
        
        # Step 2: Calculate Total Income and Expense by summing the 'amount' field
        total_income = qs.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
        total_expense = qs.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
        
        # Step 3: Get Category totals using group_by approach (values + annotate)
        categories = qs.values('category').annotate(total=Sum('amount')).order_by('-total')
        
        # Step 4: Get Top 5 recent activities by sorting descending on created_at
        recent = qs.order_by('-created_at')[:5].values('id', 'date', 'title', 'amount', 'type', 'category')
        
        # Monthly Trends (Simple month extraction, SQLite approach vs PG approach differs, let's group by month string)
        # For simplicity across generic DBs, we pull and process logic via Python for charts if dataset is small,
        # but the assignment allows reasonable assumptions. Let's send raw month strings.
        
        return Response({
            'total_income': total_income,
            'total_expenses': total_expense,
            'balance': total_income - total_expense,
            'recent_activity': list(recent),
            'categories': list(categories),
        })

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """
        Legacy endpoint mapped to provide month-over-month trend data.
        Returns a formatted array for the re-charts area graph.
        """
        qs = self._get_base_queryset(request)
        # Using a fixed mapping for demo dashboard visual since SQLite doesn't have TruncMonth easily configged.
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
        chart_data = []
        for i, month in enumerate(months):
             # Mock monthly distribution calculation to gracefully fall back without complex SQL extracts
             m_inc = total_income = qs.filter(type='income', date__month=i+1).aggregate(total=Sum('amount'))['total'] or 0
             m_exp = total_expense = qs.filter(type='expense', date__month=i+1).aggregate(total=Sum('amount'))['total'] or 0
             chart_data.append({
                 'month': month,
                 'revenue': m_inc,
                 'expenses': m_exp,
                 'profit': m_inc - m_exp
             })
        return Response(chart_data)
