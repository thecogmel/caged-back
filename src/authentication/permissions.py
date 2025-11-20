from rest_framework.permissions import BasePermission
from .models import User


class IsSpeakerPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Roles.SPEAKER


class IsFinancePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Roles.FINANCE


class IsFollowUpPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Roles.FOLLOW_UP


class IsRegistrationPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Roles.REGISTRATION


class IsLogisticsPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Roles.LOGISTICS


class IsAdminOrSupportPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in [User.Roles.ADMIN, User.Roles.SUPPORT]


class IsSuperUserPermission(BasePermission):
    message = "Apenas superusers podem executar esta ação."

    def has_permission(self, request, view=None):
        user = getattr(request, "user", None)
        return bool(
            user
            and getattr(user, "is_authenticated", False)
            and getattr(user, "is_superuser", False)
        )
