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