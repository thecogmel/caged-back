from rest_framework import status
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from django.http import Http404
from django_filters import rest_framework as django_filters
from .models import User, Profile
from .serializers import (
    UserProfileSerializer,
    ProfileSerializer,
    ProfileAuthorSerializer,
    UserImageSerializer,
    ChangePasswordSerializer,
    ActiveUserSerializer,
    ProfileIsAdminSerializer,
)
from .permissions import HasModelPermission, IsProfileOwner
from .pagination import AccountPagination

class UserProfileViewSet(ModelViewSet):
    permission_classes = [HasModelPermission]
    serializer_class = UserProfileSerializer
    http_method_names = ['get', 'post', 'head', 'put', 'patch']
    pagination_class = AccountPagination
    queryset = User.objects.all().order_by('date_joined')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, django_filters.DjangoFilterBackend]
    module_name = 'user'

    search_fields = [
        'email',
        'profile__first_name',
        'profile__last_name',
        'profile__phone_number',
        'profile__address',
        'profile__number',
        'profile__neighborhood',
        'profile__complement',
        'profile__zip_code',
        'profile__is_admin',
    ]

    ordering_fields = [
        'email',
        'is_active',
        'profile__first_name',
        'profile__last_name',
        'profile__phone_number',
        'profile__address',
        'profile__number',
        'profile__neighborhood',
        'profile__complement',
        'profile__zip_code',
        'profile__is_admin',
    ]

    filterset_fields = {
        'is_active': ['exact'],
        'profile__is_admin': ['exact'],
    }

class ProfileDetail(GenericAPIView):
    permission_classes = [HasModelPermission, IsProfileOwner]
    serializer_class = ProfileSerializer

    def get_object(self, id):
        try:
            return Profile.objects.get(user__uuid=id)
        except Profile.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        profile = self.get_object(id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        profile = self.get_object(id)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        profile = self.get_object(id)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChangePasswordView(UpdateAPIView):
    permission_classes = [HasModelPermission, IsProfileOwner]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response({
                'status': 'success',
                'message': 'Password updated successfully',
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserImageView(GenericAPIView):
    permission_classes = [HasModelPermission, IsProfileOwner]
    serializer_class = UserImageSerializer

    def get_object(self):
        try:
            return Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        profile = self.get_object()
        serializer = UserImageSerializer(profile)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        profile = self.get_object()
        serializer = UserImageSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'User image updated successfully',
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        profile = self.get_object()
        profile.image.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ActivateUserView(UpdateAPIView):
    permission_classes = [HasModelPermission]
    serializer_class = ActiveUserSerializer

    def get_object(self, id):
        try:
            return User.objects.get(uuid=id)
        except User.DoesNotExist:
            raise Http404

    def update(self, request, id, *args, **kwargs):
        user = self.get_object(id)
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileAuthorViewSet(ModelViewSet):
    http_method_names = ['get', 'options', 'head']
    permission_classes = [HasModelPermission]
    serializer_class = ProfileAuthorSerializer
    pagination_class = AccountPagination
    queryset = Profile.objects.all().order_by('pk')
    module_name = 'user'

class ProfileIsAdminViewSet(ModelViewSet):
    permission_classes = [HasModelPermission]
    serializer_class = ProfileIsAdminSerializer
    http_method_names = ['put', 'patch']
    queryset = Profile.objects.all().order_by('pk')
    module_name = 'user'