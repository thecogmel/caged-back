from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()

READ_METHODS = ['GET', 'HEAD', 'OPTIONS']
WRITE_METHODS = ['POST']
EDIT_METHODS = ['PUT', 'PATCH']
DELETE_METHODS = ['DELETE']

class IsAuthenticatedOrWriteOnly(BasePermission):
    """
    Allows unauthenticated POST requests (e.g., for registration) but requires
    authentication for other methods.
    """
    def has_permission(self, request, view):
        return bool(
            request.method in WRITE_METHODS or
            request.user and request.user.is_authenticated
        )

class IsProfileOwner(BasePermission):
    """
    Allows access if the user owns the profile object (obj.user == request.user).
    """
    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'user') and obj.user == request.user

class HasModelPermission(BasePermission):
    """
    Checks module-specific permissions based on the user's profile.
    Requires a 'module_name' attribute on the view or defaults to 'user'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # Get module name from view or default to 'user'
        module_name = getattr(view, 'module_name', 'user')

        try:
            profile = request.user.profile
            if not profile:
                return False
        except User.profile.RelatedObjectDoesNotExist:
            return False

        permission_map = {
            READ_METHODS: 'permission_read',
            WRITE_METHODS: 'permission_write',
            EDIT_METHODS: 'permission_update',
            DELETE_METHODS: 'permission_delete',
        }

        for methods, permission in permission_map.items():
            if request.method in methods:
                return profile.get_permission_for_app(module_name, permission)

        return False

class HasOtherPermission(BasePermission):
    """
    Checks permissions for a specific module (e.g., 'order', 'company').
    Requires a 'module_name' attribute on the view.
    Allows read access if any permission (read, write, edit, delete) is granted.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # Get module name from view
        module_name = getattr(view, 'module_name', None)
        if not module_name:
            return False

        try:
            profile = request.user.profile
            if not profile:
                return False
        except User.profile.RelatedObjectDoesNotExist:
            return False

        modules_permissions = profile.get_permissions_for_modules()

        if module_name not in modules_permissions:
            return False

        if request.method in READ_METHODS:
            return any([
                modules_permissions[module_name]['can_read'],
                modules_permissions[module_name]['can_write'],
                modules_permissions[module_name]['can_edit'],
                modules_permissions[module_name]['can_delete'],
            ])

        return False