from django.db.models.signals import post_save
from django.dispatch import receiver

from notification.models import Notification

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification, dispatch_uid='notification.notification.post_save_send_push')
def send_notification(sender, instance, created, **kwargs):

    print('notification.notification.post_save_send_push')
    logger.info('notification.notification.post_save_send_push:\n\n{}'.format(instance.title))

    pass
