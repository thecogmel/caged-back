from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from django.http import Http404
from .models import ProfilePermissions
from .serializers import ProfilePermissionSerializer, ProfilePermissionBasicSerializer, UserAddProfileSerializer
from .permissions import HasModelPermission
from .pagination import PermissionPagination

class ProfilePermissionViewSet(ModelViewSet):
    permission_classes = [HasModelPermission]
    http_method_names = ['get', 'post', 'head', 'put', 'patch', 'delete']
    pagination_class = PermissionPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    module_name = 'Permission'

    def get_serializer_class(self):
        if self.action == 'list':
            return ProfilePermissionBasicSerializer
        return ProfilePermissionSerializer

    def get_queryset(self):
        return ProfilePermissions.objects.all().order_by('pk')

class UserAddOrRemoveProfileView(UpdateAPIView):
    permission_classes = [HasModelPermission]
    serializer_class = UserAddProfileSerializer
    module_name = 'Permission'

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response({
            'status': 'success',
            'message': f"Permission {'removed from' if serializer.validated_data['to_remove'] else 'assigned to'} user successfully",
            'profile': ProfilePermissionBasicSerializer(profile.permission).data if profile.permission else None
        }, status=status.HTTP_200_OK)