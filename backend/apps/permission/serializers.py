from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ProfilePermissions, PermissionOptions
from apps.accounts.models import Profile

User = get_user_model()

class PermissionOptionsSerializer(serializers.ModelSerializer):
    app_option = serializers.ChoiceField(choices=PermissionOptions.APPS_CHOICES)

    class Meta:
        model = PermissionOptions
        fields = [
            'app_option',
            'permission_read',
            'permission_write',
            'permission_update',
            'permission_delete',
        ]

    def validate(self, data):
        """
        Ensure app_option is unique for the profile.
        """
        profile = self.context.get('profile')
        if profile and not self.instance:
            if PermissionOptions.objects.filter(profile=profile, app_option=data['app_option']).exists():
                raise serializers.ValidationError({
                    'app_option': f"Permission option for '{data['app_option']}' already exists for this profile."
                })
        return data

class ProfilePermissionSerializer(serializers.ModelSerializer):
    options = PermissionOptionsSerializer(many=True)

    class Meta:
        model = ProfilePermissions
        fields = ['id', 'name', 'description', 'options']

    def validate(self, data):
        """
        Ensure name is unique and options are valid.
        """
        name = data.get('name')
        if name and not self.instance and ProfilePermissions.objects.filter(name=name).exists():
            raise serializers.ValidationError({
                'name': f"A permission with name '{name}' already exists."
            })
        return data

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        profile = ProfilePermissions.objects.create(**validated_data)
        for option_data in options_data:
            PermissionOptions.objects.create(
                profile=profile,
                **option_data
            )
        return profile

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Update or create PermissionOptions
        for option_data in options_data:
            app_option = option_data.get('app_option')
            option, created = PermissionOptions.objects.get_or_create(
                profile=instance,
                app_option=app_option,
                defaults=option_data
            )
            if not created:
                option.permission_read = option_data.get('permission_read', option.permission_read)
                option.permission_write = option_data.get('permission_write', option.permission_write)
                option.permission_update = option_data.get('permission_update', option.permission_update)
                option.permission_delete = option_data.get('permission_delete', option.permission_delete)
                option.save()

        return instance

class ProfilePermissionBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePermissions
        fields = ['id', 'name', 'description']

class UserAddProfileSerializer(serializers.Serializer):
    user_uuid = serializers.UUIDField(required=True)
    permission_id = serializers.PrimaryKeyRelatedField(
        queryset=ProfilePermissions.objects.all(),
        required=True
    )
    to_remove = serializers.BooleanField(default=False)

    def validate_user_uuid(self, value):
        try:
            user = User.objects.get(uuid=value)
            if not hasattr(user, 'profile') or user.profile is None:
                raise serializers.ValidationError("User does not have a profile.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this UUID does not exist.")

    def save(self):
        user_uuid = self.validated_data['user_uuid']
        permission = self.validated_data['permission_id']
        to_remove = self.validated_data['to_remove']
        user = User.objects.get(uuid=user_uuid)
        profile = user.profile

        if to_remove:
            profile.permission = None
        else:
            profile.permission = permission
        profile.save()
        return profile