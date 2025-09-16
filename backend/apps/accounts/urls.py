from django.urls import include, path
from rest_framework import routers
from .views import (
    UserProfileViewSet,
    ProfileDetail,
    UserImageView,
    ChangePasswordView,
    ActivateUserView,
    ProfileAuthorViewSet,
    ProfileIsAdminViewSet,
)

app_name = 'accounts'

router = routers.DefaultRouter()
router.register(r'users', UserProfileViewSet, basename='user')
router.register(r'authors', ProfileAuthorViewSet, basename='profile-author')
router.register(r'profile-admin', ProfileIsAdminViewSet, basename='profile-admin')

urlpatterns = [
    path('', include(router.urls)),
    path('users/activate/<uuid:id>/', ActivateUserView.as_view(), name='user-activate'),
    path('profiles/<uuid:id>/', ProfileDetail.as_view(), name='profile-detail'),
    path('users/change-password/<uuid:id>/', ChangePasswordView.as_view(), name='user-change-password'),
    path('profiles/photo/<uuid:id>/', UserImageView.as_view(), name='profile-photo'),
]