from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from .models import User, Profile
from apps.permission.serializers import ProfilePermissionBasicSerializer
from apps.address.serializers import (
    CountrySerializer,
    StateSerializer,
    CitySerializer,
    AddressTypeSerializer,
)

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    permission_set = ProfilePermissionBasicSerializer(source='permission', read_only=True)
    country_set = CountrySerializer(source='country', read_only=True)
    state_set = StateSerializer(source='state', read_only=True)
    city_set = CitySerializer(source='city', read_only=True)
    address_type_set = AddressTypeSerializer(source='address_type', read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'image',
            'is_admin',
            'permission',
            'permission_set',
            'address',
            'address_type',
            'address_type_set',
            'number',
            'neighborhood',
            'complement',
            'city',
            'city_set',
            'state',
            'state_set',
            'country',
            'country_set',
            'zip_code',
            'get_full_name',
            'get_uuid',
            'get_email',
            'is_active',
            'permissions',
        ]
        read_only_fields = ['get_full_name', 'get_uuid', 'get_email', 'is_active']

    def get_permissions(self, obj):
        return obj.get_permissions_for_modules()

class ProfileBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'get_full_name', 'get_uuid']
        read_only_fields = ['get_full_name', 'get_uuid']

class ProfileToOrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'get_full_name']
        read_only_fields = ['get_full_name']

class ProfileAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'get_full_name', 'get_uuid', 'is_active']
        read_only_fields = ['get_full_name', 'get_uuid', 'is_active']

class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = [
            'uuid',
            'email',
            'is_active',
            'is_superuser',
            'profile',
            'password',
        ]
        extra_kwargs = {'password': {'write_only': True}, 'is_active': {'read_only': True}}

    def validate(self, data):
        profile_data = data.get('profile', {})
        if self.instance is None and not profile_data.get('first_name'):
            raise serializers.ValidationError({"profile": {"first_name": "This field is required."}})
        if self.instance is None and not profile_data.get('last_name'):
            raise serializers.ValidationError({"profile": {"last_name": "This field is required."}})
        if self.instance is None and not profile_data.get('phone_number'):
            raise serializers.ValidationError({"profile": {"phone_number": "This field is required."}})
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data.get('password'),
            is_superuser=validated_data.get('is_superuser', False),
            is_staff=validated_data.get('is_superuser', False),  # Staff status tied to superuser for simplicity
        )
        profile = user.profile  # Created automatically via post_save signal
        for field, value in profile_data.items():
            if value is not None:
                setattr(profile, field, value)
        profile.save()
        return user

    def update(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = self.instance
        user.email = validated_data.get('email', user.email)
        if validated_data.get('password'):
            user.set_password(validated_data['password'])
        user.is_superuser = validated_data.get('is_superuser', user.is_superuser)
        user.is_staff = validated_data.get('is_superuser', user.is_staff)  # Sync staff status
        user.save()
        profile = user.profile
        for field, value in profile_data.items():
            if value is not None:
                setattr(profile, field, value)
        profile.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

class UserImageSerializer(serializers.Serializer):
    image = Base64ImageField(required=True, represent_in_base64=True)

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

class ProfileIsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'is_admin']

class ActiveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'is_active',
        ]