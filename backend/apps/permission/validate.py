from django.contrib.auth import get_user_model
from apps.accounts.models import Profile
from rest_framework import serializers

User = get_user_model()

def validate_permission(uuid, app_option, has_permission):
    """
    Check if a user with the given UUID has the specified permission for an app_option.
    
    Args:
        uuid: UUID of the user.
        app_option: The app/module to check (e.g., 'User', 'Permission').
        has_permission: The permission to verify ('permission_read', 'permission_write', 
                        'permission_update', 'permission_delete').
    
    Returns:
        bool: True if the user has the permission, False otherwise.
    
    Raises:
        serializers.ValidationError: If the user doesn't exist or the permission is invalid.
    """
    try:
        profile = Profile.objects.get(user__uuid=uuid)
    except Profile.DoesNotExist:
        raise serializers.ValidationError(f"User with UUID {uuid} does not exist.")

    if profile.user.is_superuser or profile.user.is_staff or profile.is_admin:
        return True

    if has_permission not in ['permission_read', 'permission_write', 'permission_update', 'permission_delete']:
        raise serializers.ValidationError(f"Invalid permission: {has_permission}")

    return profile.get_permission_for_app(app_option, has_permission)