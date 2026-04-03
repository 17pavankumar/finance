from rest_framework import permissions

class IsAdminUserRole(permissions.BasePermission):
    """
    Allows access only to users with the 'admin' role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'profile') and 
            request.user.profile.role == 'admin'
        )

class IsAnalystOrAdmin(permissions.BasePermission):
    """
    Allows full access to admins, and read-only access to analysts.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated or not hasattr(request.user, 'profile'):
            return False
            
        role = request.user.profile.role
        if role == 'admin':
            return True
            
        if role == 'analyst' and request.method in permissions.SAFE_METHODS:
            return True
            
        return False

class IsViewer(permissions.BasePermission):
    """
    Allows read-only access strictly for viewers (mostly for dashboard).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated or not hasattr(request.user, 'profile'):
            return False
            
        role = request.user.profile.role
        if role in ['admin', 'analyst', 'viewer'] and request.method in permissions.SAFE_METHODS:
            return True
            
        return False
