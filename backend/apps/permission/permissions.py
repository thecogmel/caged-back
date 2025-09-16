from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

from apps.permission.validate import validate_permission

# User = get_user_model()

READ_METHOD = ['GET', 'HEAD', 'OPTIONS']
WRITE_METHOD = ['POST']
EDIT_METHOD = ['PUT', 'PATCH']
DELETE_METHOD = ['DELETE']
MODEL_NAME = 'Permission'


class IsAuthenticatedOrWriteOnly(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.method in WRITE_METHOD or
            request.user and request.user.is_authenticated
        )


class HasModelPermission(BasePermission):

    def has_profile_permission(self, user, app_option, has_permission):

        return validate_permission(user.uuid, app_option, has_permission)

    def has_permission(self, request, view):

        if request.user.is_superuser:
            return True

        if request.method in READ_METHOD:
            is_true = self.has_profile_permission(user=request.user,
                                                  app_option=MODEL_NAME,
                                                  has_permission="permission_read")
            return is_true

        if request.method in WRITE_METHOD:
            is_true = self.has_profile_permission(user=request.user,
                                                  app_option=MODEL_NAME,
                                                  has_permission="permission_write")
            return is_true

        if request.method in EDIT_METHOD:
            is_true = self.has_profile_permission(user=request.user,
                                                  app_option=MODEL_NAME,
                                                  has_permission="permission_update")
            return is_true

        if request.method in DELETE_METHOD:
            is_true = self.has_profile_permission(user=request.user,
                                                  app_option=MODEL_NAME,
                                                  has_permission="permission_delete")
            return is_true

        return False
