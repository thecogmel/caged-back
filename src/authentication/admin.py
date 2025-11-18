from django.contrib import admin

from .models import User


# Register your models here.
class AuthenticationAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = (
        "id",
        "name",
        "email",
        "role",
        "is_active",
        "is_staff",
    )


admin.site.register(User, AuthenticationAdmin)
