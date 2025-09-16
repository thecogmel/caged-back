from django.contrib import admin
from .models import PermissionOptions, ProfilePermissions


class PermissionOptionsInline(admin.TabularInline):
    model = PermissionOptions


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    inlines = (PermissionOptionsInline,)


admin.site.register(ProfilePermissions, ProfileAdmin)
