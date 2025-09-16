from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .views import (
        CountryViewSet,
        StateViewSet,
        CityViewSet,
        AddressTypeViewSet,
        NeighborhoodTypeViewSet,
)

app_name = 'address'

router = SimpleRouter()
router.register(r'country', CountryViewSet, basename="country")
router.register(r'state', StateViewSet, basename="state")
router.register(r'city', CityViewSet, basename="city")
router.register(r'address-type', AddressTypeViewSet, basename="address_type")
router.register(r'neighborhood-type', NeighborhoodTypeViewSet, basename="neighborhood_type")

urlpatterns = [
    path('', include(router.urls)),
]
