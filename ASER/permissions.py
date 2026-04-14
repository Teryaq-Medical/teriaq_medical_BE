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
    """
    Allows read access to anyone.
    Write access only for admins and authenticated users who belong to a medical entity
    (hospitals, clinics, labs, doctors).
    """
    def has_permission(self, request, view):
        # Read-only for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin can do anything
        if request.user and request.user.is_staff:
            return True

        # Write access only for authenticated medical entities
        allowed_types = ['hospitals', 'clincs', 'labs', 'doctors']
        return (
            request.user.is_authenticated and
            request.user.user_type in allowed_types
        )
        
        

# ASER/permissions.py
from rest_framework import permissions

class IsLabOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        # For POST, we'll check in perform_create
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        # Check if the requesting user owns the lab that this specialist belongs to
        if hasattr(obj, 'lab') and hasattr(obj.lab, 'user'):
            return obj.lab.user == request.user
        return False