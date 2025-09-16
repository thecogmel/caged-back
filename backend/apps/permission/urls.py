from django.urls import include, path
from rest_framework import routers
from .views import ProfilePermissionViewSet, UserAddOrRemoveProfileView

app_name = 'permission'

router = routers.DefaultRouter()
router.register(r'permissions', ProfilePermissionViewSet, basename='permission')

urlpatterns = [
    path('', include(router.urls)),  # Handles /permissions/ (list, create) and /permissions/<id>/ (retrieve, update, delete)
    path('permissions/add-user/', UserAddOrRemoveProfileView.as_view(), name='add-or-remove-user'),  # Handles assigning/removing permissions
]