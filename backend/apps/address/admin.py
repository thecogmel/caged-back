from import_export.admin import ImportExportMixin
from django.contrib import admin
from .models import (
        Country,
        State,
        City,
        AddressType,
        NeighborhoodType,
)

class CountryAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = [
            'name',
            'code',
        ]

class StateAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = [
            'name',
            'code',
            'country',
        ]

class CityAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = [
            'name',
            'code',
            'state',
        ]

class AddressTypeAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = [
            'name',
        ]


class NeighborhoodTypeAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = [
            'name',
        ]

admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(AddressType, AddressTypeAdmin)
admin.site.register(NeighborhoodType, NeighborhoodTypeAdmin)
