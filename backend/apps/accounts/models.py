import uuid
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from apps.utils.phone_validator import phone_regex
from apps.address.models import AddressType, City, State, Country
from .managers import UserManager  # Import the UserManager from managers.py

class User(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), max_length=150, editable=False, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()  # Use the imported UserManager

    class Meta:
        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['email']),
        ]

# The rest of your models.py (Profile, signals, etc.) remains unchanged
class Profile(models.Model):
    def validate_image_size(field_file):
        file_size = field_file.file.size
        megabyte_limit = 5.0
        if file_size > megabyte_limit * 1024 * 1024:
            raise ValidationError('Max file size is 5MB')

    def upload_to_path(self, filename):
        ext = filename.split('.')[-1]
        name = uuid.uuid4().hex
        return f'profile/{name}.{ext}'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(verbose_name="first_name", max_length=255, blank=False)
    last_name = models.CharField(verbose_name="last_name", max_length=255, blank=False)
    phone_number = models.CharField(verbose_name="phone", validators=[phone_regex], max_length=17, blank=False)
    image = models.ImageField(upload_to=upload_to_path, blank=True, null=True, validators=[validate_image_size])
    is_admin = models.BooleanField(default=False)
    permission = models.ForeignKey('permission.ProfilePermissions', on_delete=models.PROTECT, related_name='user', blank=True, null=True)
    address_type = models.ForeignKey(AddressType, on_delete=models.PROTECT, blank=True, null=True)
    address = models.CharField(verbose_name="address", max_length=255, blank=True, null=True)
    number = models.CharField(verbose_name="number", max_length=50, blank=True, null=True)
    neighborhood = models.CharField(verbose_name="neighborhood", max_length=50, blank=True, null=True)
    complement = models.CharField(verbose_name="complement", max_length=1050, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.PROTECT, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
    zip_code = models.CharField(verbose_name="CEP", max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.user.email}'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_permission_for_app(self, app, action):
        if self.user.is_superuser or self.user.is_staff or self.is_admin:
            return True
        if self.permission:
            permission = self.permission.options.filter(app_option=app).first()
            if permission:
                return getattr(permission, action, False)
        return False

    def get_permissions_for_modules(self):
        MODULES = (
            ('user', 'User'),
            ('permission', 'Permission'),
            ('company', 'Company'),
            ('checklist', 'Checklist'),
            ('order', 'Order'),
            ('order_settings', 'OrderSettings'),
            ('partner', 'Partner'),
            ('partner_settings', 'PartnerSettings'),
            ('stock', 'Stock'),
            ('stock_settings', 'StockSettings'),
            ('product', 'Product'),
            ('product_settings', 'ProductSettings'),
            ('supplier', 'Supplier'),
            ('report', 'Report'),
            ('report_settings', 'ReportSettings'),
            ('admin', 'Admin'),
        )
        PERMISSIONS = (
            ('can_read', 'permission_read'),
            ('can_edit', 'permission_update'),
            ('can_write', 'permission_write'),
            ('can_delete', 'permission_delete'),
        )
        permissions_modules = {}
        for key, value in MODULES:
            permissions_modules[key] = {}
            for action, permission in PERMISSIONS:
                permissions_modules[key][action] = self.get_permission_for_app(value, permission)
        return permissions_modules

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()