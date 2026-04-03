import pandas as pd
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import FinanceRecord
from .serializers import FinanceRecordSerializer
from users.permissions import IsAnalystOrAdmin

class FinanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = FinanceRecordSerializer
    permission_classes = [IsAnalystOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'type', 'date']

    def get_queryset(self):
        # Admin can view all records across all users
        if self.request.user.profile.role == 'admin':
            return FinanceRecord.objects.all().order_by('-date')
        # Analyst can only view their own assigned data (or perhaps all data, depending on logic)
        # Let's say analysts can view all data globally to provide insights, but can't modify.
        # Based on scenario: "Analyst can view records and access insights". Let's give them global read.
        return FinanceRecord.objects.all().order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            df = pd.read_csv(file)
            
            # Simple Column validation
            required_columns = {'date', 'title', 'category', 'amount', 'type'}
            if not required_columns.issubset(set(df.columns)):
                return Response(
                    {'error': f'Missing required columns. Found {list(df.columns)}, expected {required_columns}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            records = []
            errors = []
            
            for index, row in df.iterrows():
                amount = row.get('amount')
                # Input validation
                try: 
                    amount = float(amount)
                    if amount <= 0:
                        raise ValueError("Amount must be positive")
                except (ValueError, TypeError):
                    errors.append(f"Row {index+1}: Invalid amount '{amount}'")
                    continue
                    
                entry_type = str(row.get('type')).lower()
                if entry_type not in ['income', 'expense']:
                    errors.append(f"Row {index+1}: Invalid type '{entry_type}'. Must be income/expense.")
                    continue

                record = FinanceRecord(
                    user=request.user,
                    date=row.get('date'),
                    title=row.get('title'),
                    category=row.get('category'),
                    amount=amount,
                    type=entry_type,
                    description=row.get('description', '')
                )
                records.append(record)
                
            if errors:
                return Response({
                    'error': 'Validation failed for some rows',
                    'details': errors[:5] # Return first 5 errors to avoid massive payloads
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                
            FinanceRecord.objects.bulk_create(records)
            return Response({'message': f'Successfully uploaded {len(records)} records'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'System error processing file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        import csv
        from django.http import HttpResponse
        
        records = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="finance_records.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Title', 'Category', 'Amount', 'Type', 'User'])
        
        for record in records:
            writer.writerow([
                record.date, record.title, record.category, 
                record.amount, record.type, record.user.username
            ])
            
        return response
