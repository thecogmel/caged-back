from django.contrib import admin

from .models import Gathering


class GatheringAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = (
        "id",
        "name",
        "date",
        "location",
        "description",
    )


admin.site.register(Gathering, GatheringAdmin)
