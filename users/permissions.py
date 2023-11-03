from rest_framework import permissions


class IsExecutiveSecretary(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_executive  # TODO: check permissions


class IsParty(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a party
        return request.user.is_party


class IsStaffUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is staff
        return request.user.is_staff


class OwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.created_by == request.user


class AssignTasks(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
    # Check permissions for read-only request
        else:
            # Check permissions for write request
            return obj.assigned_by == request.user


class ReadOnlyOrPartialUpdatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow GET and PATCH requests, deny all others
        if request.method in ('GET', 'PATCH'):
            return True
        return False


class CanUpdateField(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow read access (GET) to all fields
        if request.method in permissions.SAFE_METHODS:
            return True
        # Restrict write access (PATCH) to the specific field you want to update
        return request.data.keys() == {'is_verified'}
