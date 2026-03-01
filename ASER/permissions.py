from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit/delete objects.
    Anyone can view (GET).
    """
    def has_permission(self, request, view):
        # Allow any safe request (GET, HEAD or OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users
        return bool(request.user and request.user.is_staff)
    
class IsAdminOrMedicalEntity(permissions.BasePermission):

    def has_permission(self, request, view):

        # Anyone can GET
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin full access
        if request.user and request.user.is_staff:
            return True

        # Only hospital/clinic/lab can write
        allowed_types = ['hospital', 'clinic', 'lab']

        return (
            request.user.is_authenticated and
            request.user.user_type in allowed_types
        )
