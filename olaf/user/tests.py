from django.test import TestCase, Client
from django.shortcuts import reverse
from django.db.models import signals
from django.contrib.auth import get_user_model

from olaf.tasks import send_sms_to

import json

User = get_user_model()


class SignalTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(phone_number='994508874380', password='12345')

    def test_order_list_view_GET(self):

        self.assertIsNotNone(self.user.profile)

        self.assertIsNotNone(self.user.notifications)


class TFATests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(phone_number='994508874380', password='12345')

        self.client.login(phone_number='994508874380', password='12345')

    def test_request_tfa(self):
        pass
        # send_sms_to('508874380')

    def test_request_tfa_view(self):

        data = {
            'phone_number': '508874380'
        }

        url = reverse('user:request-tfa')

        response = self.client.post(url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
