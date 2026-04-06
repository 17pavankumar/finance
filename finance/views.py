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
            filename = file.name.lower()
            df = pd.read_excel(file) if filename.endswith(('.xlsx', '.xls')) else pd.read_csv(file)
            
            # Normalize column matching strictly 
            df.columns = df.columns.str.strip().str.lower()
            
            # Pure unpacking object instantiation
            records = [
                FinanceRecord(user=request.user, **row) 
                for row in df.to_dict('records')
            ]
            
            FinanceRecord.objects.bulk_create(records)
            return Response({'message': f'Successfully uploaded {len(records)} neat records'}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': f'System syntax error processing: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

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
