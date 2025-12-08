from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db import models
from model_utils.models import TimeStampedModel

from .managers import UserManager


class User(TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        SUPPORT = "SUPPORT", "Suporte"
        SPEAKER = "SPEAKER", "Palestra"
        FINANCE = "FINANCE", "Finanças"
        FOLLOW_UP = "FOLLOW_UP", "Pós-encontro"
        REGISTRATION = "REGISTRATION", "Fichas"
        LOGISTICS = "LOGISTICS", "Montagem"
        MEMBER = "MEMBER", "Membro"

    name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=Roles.choices, default=Roles.MEMBER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = UserManager()
    REQUIRED_FIELDS = ["name", "username"]

    def __str__(self):
        return self.email
