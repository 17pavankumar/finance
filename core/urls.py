from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({"message": "Welcome to the Finance API. Frontend is running on Vite port 5173."})

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/finance/', include('finance.urls')),
]
