from django_filters import rest_framework as django_filters
from rest_framework import filters
from rest_framework import status
from rest_framework.response import Response
from apps.utils.cache import ModelViewSetCached

from .pagination import AddressPagination
from .models import (
        Country,
        State,
        City,
        AddressType,
        NeighborhoodType,
)
from .serializers import (
        CountrySerializer,
        StateSerializer,
        CitySerializer,
        AddressTypeSerializer,
        NeighborhoodTypeSerializer,
)
from .permissions import (
        IsAuthenticated,
)

class CountryViewSet(ModelViewSetCached):
    http_method_names = ['get', 'head']
    serializer_class = CountrySerializer
    permission_classes = ( IsAuthenticated,)
    pagination_class = AddressPagination
    queryset = Country.objects.all().order_by('pk')
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'code',
        'name',
        ]

    def get_queryset(self):
        return Country.objects.all().order_by('pk')
    
class StateViewSet(ModelViewSetCached):
    http_method_names = ['get', 'head']
    serializer_class = StateSerializer
    permission_classes = ( IsAuthenticated,)
    pagination_class = AddressPagination
    queryset = State.objects.all().order_by('pk')
    filter_backends = [filters.SearchFilter,
                       django_filters.DjangoFilterBackend]
    search_fields = [
        'code',
        'name',
        ]

    filter_fields = {
            'country': ['exact'],
    }

    def get_queryset(self):
        return State.objects.all().order_by('pk')
    
class CityViewSet(ModelViewSetCached):
    http_method_names = ['get', 'head']
    serializer_class = CitySerializer
    permission_classes = ( IsAuthenticated,)
    pagination_class = AddressPagination
    queryset = City.objects.all().order_by('pk')
    filter_backends = [filters.SearchFilter,
                       django_filters.DjangoFilterBackend]
    search_fields = [
        'code',
        'name',
        ]

    filter_fields = {
            'state': ['exact'],
    }

    def get_queryset(self):
        return City.objects.all().order_by('pk')

class AddressTypeViewSet(ModelViewSetCached):
    http_method_names = ['get', 'head', 'options', 'put', 'delete', 'post']
    serializer_class = AddressTypeSerializer
    permission_classes = ( IsAuthenticated,)
    pagination_class = AddressPagination
    queryset = AddressType.objects.all().order_by('pk')
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'id',
        'name',
    ]

    def get_queryset(self):
        return AddressType.objects.all().order_by('pk')

class NeighborhoodTypeViewSet(ModelViewSetCached):
    http_method_names = ['get', 'head']
    serializer_class = NeighborhoodTypeSerializer
    permission_classes = ( IsAuthenticated,)
    pagination_class = AddressPagination
    queryset = NeighborhoodType.objects.all().order_by('pk')
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'name',
        ]

    def get_queryset(self):
        return NeighborhoodType.objects.all().order_by('pk')
