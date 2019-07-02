from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from user.managers import UserManager
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin
)

from django.contrib.gis.db import models as gis_models


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    """
    # Local numbers only. for now
    phone_number_validator = RegexValidator(regex='^\d{9}$', message='Length has to be 9', code='nomatch')

    phone_number = models.CharField(max_length=20, validators=[phone_number_validator], unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    is_business = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'

    class Meta:
        verbose_name = 'Olaf User'
        verbose_name_plural = 'Olaf Users'

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self

    def __str__(self):
        return self.phone_number


class UserProfile(models.Model):

    email_address = models.EmailField(max_length=40, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)

    AZ = "AZ"
    RU = "RU"
    EN = "EN"

    LANGUAGE_CHOICES = (
        (AZ, "az-AZ"),
        (RU, "ru-RU"),
        (EN, "en-EN"),
    )

    preferred_language = models.CharField(max_length=15, choices=LANGUAGE_CHOICES, default=AZ)
    subscribed_to_email = models.BooleanField(default=False)

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE, primary_key=True)

    @property
    def total_order_count(self):
        from order.models import Order

        return Order.manager.confirmed().filter(user=self.user).count()

    @property
    def total_order_amount(self):
        from order.models import Order

        total_price = 0
        for order in Order.manager.confirmed().filter(user=self.user):
            total_price += order.total_price
        return total_price

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return ' '.join([self.first_name, self.last_name])
        return ''

    class Meta:
        verbose_name = 'Olaf User Profile'
        verbose_name_plural = 'Olaf User Profiles'


class Device(models.Model) :

    ANDROID = 'android'
    IOS = 'ios'

    DEVICE_OS_CHOICES = (
        (ANDROID, 'Android'),
        (IOS, 'iOS')
    )

    device_id = models.CharField(unique=True, max_length=1024, default='')
    device_type = models.SmallIntegerField(choices=DEVICE_OS_CHOICES, blank=True, null=True)
    user = models.ForeignKey(User, related_name='devices', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'User Device'
        verbose_name_plural = 'User Devices'


class UserActivity(models.Model):
    user = models.OneToOneField(User, related_name='activity', on_delete=models.CASCADE, primary_key=True)
    date = models.DateTimeField(auto_now=True)

    gis_location = gis_models.PointField(_('Location'))

    @property
    def location(self):
        return {
            'latitude': self.gis_location.y,
            'longitude': self.gis_location.x
        }

    def __str__(self):
        return self.user.__str__() + '\t|\t' + str(self.date)

    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'


class FootNote(models.Model):
    user = models.ForeignKey(User, related_name='template_notes', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    message = models.TextField(max_length=200)

    def __str__(self):
        return self.name + ' :' + str(self.user.phone_number)
