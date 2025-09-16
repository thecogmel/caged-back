from rest_framework import serializers
from .models import (
        Country,
        State,
        City,
        AddressType,
        NeighborhoodType,
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    country_set = CountrySerializer(source='country', read_only=True)
    class Meta:
        model = State
        fields = [
                'id',
                'name',
                'code',
                'country',
                'country_set',
        ]

class CitySerializer(serializers.ModelSerializer):
    state_set = StateSerializer(source='state', read_only=True)
    class Meta:
        model = City
        fields = [
                'id',
                'name',
                'code',
                'state',
                'state_set',
        ]

class AddressTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressType
        fields = '__all__'

class NeighborhoodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NeighborhoodType
        fields = '__all__'
