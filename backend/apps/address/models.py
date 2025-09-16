from django.db import models

from django.db.models import (
    Model,
    CharField,
    IntegerField,
    ForeignKey,
    CASCADE,
)

class Country(Model):
    name = CharField(
            verbose_name="country_name",
            max_length=200,
            null=False,
            blank=False,
            unique=True)

    code = CharField(
            verbose_name="country_code",
            max_length=200,
            null=False,
            blank=False,
            unique=True)

class State(Model):
    name = CharField(
            verbose_name="state_name",
            max_length=200,
            null=False,
            blank=False,
            unique=True)

    code = CharField(
            verbose_name="state_code",
            max_length=200,
            null=False,
            blank=False,
            unique=True)

    country = ForeignKey(
            'Country',
            related_name="state",
            on_delete=CASCADE)

class City(Model):
    name = CharField(
            verbose_name="city_name",
            max_length=200,
            null=False,
            blank=False)

    code = CharField(
            verbose_name="city_code",
            max_length=200,
            null=False,
            blank=False,
            unique=True)

    state = ForeignKey(
            'State',
            related_name="city",
            on_delete=CASCADE)

class AddressType(Model):
    name = CharField(
            verbose_name="address_type_name",
            max_length=200,
            null=False,
            blank=False,
            unique=True)

class NeighborhoodType(Model):
    name = CharField(
            verbose_name="neighborhood_type_name",
            max_length=200,
            null=False,
            blank=False,
            unique=True)

