from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'is_active', 'is_staff', 'is_superuser']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['email']
    filter_horizontal = ['user_permissions']

    fieldsets = (
        ('Informações pessoais', {'fields': ('email', 'first_name', 'last_name')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
    )
    add_fieldsets = (
        ('Informações pessoais', {
            'fields': ('email', 'password1', 'password2')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )

    inlines = (ProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

admin.site.register(User, CustomUserAdmin)