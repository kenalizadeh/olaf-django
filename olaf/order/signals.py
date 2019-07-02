from django.db.models.signals import post_save
from django.dispatch import receiver

from olaf.tasks import handle_order

from order.models import Order


# @receiver(post_save, sender=Order, dispatch_uid='order.order.post_save')
# def handle_order(sender, instance, created, **kwargs):
#     if created:
#         print('\n\nhandle_order called on order: {}\n\n'.format(instance))
#         handle_order.apply_async((instantce.pk,), eta=timezone.now() + datetime.timedelta(minutes=10))
