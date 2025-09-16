from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token

class ProfilePermissions(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False, unique=True)
    description = models.TextField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_profile_permission_name'),
        ]

class PermissionOptions(models.Model):
    APPS_CHOICES = (
        ('Default', 'Padrão'),
        ('User', 'Usuários'),
        ('Permission', 'Permissões'),
    )

    app_option = models.CharField(
        max_length=50,
        choices=APPS_CHOICES,
        null=False,
        blank=False,
        default='Default'
    )
    permission_read = models.BooleanField(verbose_name='Visualizar', default=False)
    permission_write = models.BooleanField(verbose_name='Criar', default=False)
    permission_update = models.BooleanField(verbose_name='Atualizar', default=False)
    permission_delete = models.BooleanField(verbose_name='Apagar', default=False)
    profile = models.ForeignKey(
        'ProfilePermissions',
        on_delete=models.CASCADE,
        related_name='options'
    )

    def __str__(self):
        return f'{self.app_option}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'app_option'],
                name='unique_permission_options_profile_app'
            ),
        ]

@receiver(post_save, sender=PermissionOptions)
def logout_user_with_from_permission(sender, instance, created, **kwargs):
    if not created:
        user_list = settings.AUTH_USER_MODEL.objects.filter(profile__permission=instance.profile)
        Token.objects.filter(user__in=user_list).delete()