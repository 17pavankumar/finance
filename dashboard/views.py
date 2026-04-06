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
        from django.utils import timezone
        
        # Step 1: Get all records based on user role (Admin sees all, Viewer sees their own)
        qs = self._get_base_queryset(request)
        
        # Step 2: Calculate Total Income and Expense by summing the 'amount' field
        total_income = qs.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
        total_expense = qs.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
        
        # Step 3: Daily Expenses (Today's specifically)
        today = timezone.now().date()
        today_expense = qs.filter(type='expense', date=today).aggregate(total=Sum('amount'))['total'] or 0
        
        # Step 4: Get Category totals using group_by approach (values + annotate)
        categories = qs.values('category').annotate(total=Sum('amount')).order_by('-total')
        
        # Step 5: Get Top 5 recent activities by sorting descending on created_at
        recent = qs.order_by('-created_at')[:5].values('id', 'date', 'title', 'amount', 'type', 'category')
        
        return Response({
            'total_income': total_income,
            'total_expenses': total_expense,
            'today_expenses': today_expense,
            'balance': total_income - total_expense,
            'recent_activity': list(recent),
            'categories': list(categories),
        })

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        qs = self._get_base_queryset(request)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        chart_data = []

        for i, month_name in enumerate(months):
            month_index = i + 1  # 1 to 7

            # Calculate income for the month (default to 0 if None)
            inc_data = qs.filter(type='income', date__month=month_index).aggregate(total=Sum('amount'))
            income = inc_data['total'] or 0

            # Calculate expenses for the month (default to 0 if None)
            exp_data = qs.filter(type='expense', date__month=month_index).aggregate(total=Sum('amount'))
            expenses = exp_data['total'] or 0

            chart_data.append({
                'month': month_name,
                'revenue': income,
                'expenses': expenses,
                'profit': income - expenses
            })

        return Response(chart_data)
