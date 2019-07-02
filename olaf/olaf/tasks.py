from django.conf import settings

from celery import shared_task

from authy.api import AuthyApiClient

from order.models import Order

import requests

import logging

authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)

logger = logging.getLogger(__name__)

API_URL = 'https://onesignal.com/api/v1/notifications'

APP_ID = '7c217e2f-29c8-440a-9094-0089270415d2'

APP_REST_API_KEY = 'MmEwZWY0ZDUtOWY1Ni00MWZiLTg0MzktZjM3NDRjOTIxZDM0'


@shared_task
def handle_order(order_id):
    order = Order.objects.get(pk=order_id)

    # Instead of this. Tasks should be manually cancelled when restaurant/user responds to the order.
    # I don't think this can cause a problem but it looks shitty
    if order.status == Order.STATUS.SENT:
        order.status = Order.STATUS.REFUSED

        player_ids = list(map(lambda x: x.device_id, order.user.devices.all()))

        headers = {
            'Content-Type': 'application/json',
            'Authorization': APP_REST_API_KEY
        }

        payload = {
            'app_id': APP_ID,
            'include_player_ids': player_ids,
            'data': {'order': order.pk},
            'headings': {'en': 'Your order has been cancelled'}, # I believe this is the title
            'subtitle': {'en': 'Restaurant failed to respond to your order'}, # Subtitle
            'contents': {'en': 'Your order has been cancelled automatically'}, # Message
        }

        # don't use params, don't use data. use json otherwise data gets fucked
        # and onesignal keeps crying about language shit
        requests.post(API_URL, json=payload, headers=headers)

        order.save()


@shared_task
def send_sms_to(number):
    logger.info('Sending TFA Verification Code to number: \'{}\''.format(number))
    authy_api.phones.verification_start(
        number,
        '994',
        via='sms'
    )
