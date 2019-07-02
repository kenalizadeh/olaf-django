from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models import User, UserProfile

from notification.models import Notification


@receiver(post_save, sender=User, dispatch_uid='user.user.post_save_create_profile')
def create_profile(sender, instance, created, **kwargs):

    print('user.user.post_save_create_profile')

    if created and not instance.is_superuser:
        profile, created = UserProfile.objects.update_or_create(user=instance)


@receiver(post_save, sender=User, dispatch_uid='user.user.post_save_welcome_notification')
def welcome_notification(sender, instance, created, **kwargs):

    print('user.user.post_save_welcome_notification')

    if created and not instance.is_superuser:
        Notification.objects.create(
            title='Welcome to Olaf!',
            message='Browse the main page to place your first order.',
            user=instance
        )
