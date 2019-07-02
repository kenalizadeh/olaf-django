from django.test import TestCase, Client
from django.shortcuts import reverse
from django.db.models import signals
from django.contrib.auth import get_user_model

import json

User = get_user_model()

from django.contrib.gis import geos

from merchant.tests import generate_polygon

from user.models import UserActivity
from merchant.models import (
    Restaurant,
    MenuItemCategory,
    MenuItem,
    MenuItemOption,
    MenuItemType
)

from order.models import Order
from core.encoders import UUIDEncoder


def create_post_data(restaurant, item, item_type):
    return {
        "restaurant": restaurant.uuid,
        "footnote": "FootNote",
        "delivery_point": {
            "latitude": 40.406225,
            "longitude": 49.870523
        },
        "items": [
            {
                "id": item.uuid,
                "count": 1,
                "options": [],
                "type": item_type.uuid
            },
        ]
    }


class OrderAPITests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(phone_number='994508874380', password='12345')

        latitude = 40.402105
        longitude = 49.868889

        UserActivity.objects.create(user=self.user, gis_location=geos.Point(longitude, latitude))

        self.client.login(phone_number='994508874380', password='12345')

        self.restaurant = Restaurant.objects.create(
            title='Restaurant 1',
            description='Restaurant 1',
            gis_location=geos.Point(longitude, latitude),
            delivery_area=generate_polygon(latitude, longitude, 0.009)
        )

        self.item_category = MenuItemCategory.objects.create(name='Test Category')

        self.item = MenuItem.objects.create(
            name='Test Item',
            description='Test Item Description',
            delivery_time_min=0,
            delivery_time_max=30,
            restaurant=self.restaurant,
            category=self.item_category
        )

        self.item_type = MenuItemType.objects.create(
            name='Test Item Standard',
            price=5,
            state=True,
            menu_item=self.item
        )

        self.order_list_url = reverse('order:list')
        self.order_place_url = reverse('order:create')

    def test_order_list_view_GET(self):

        data = create_post_data(self.restaurant, self.item, self.item_type)

        self.client.post(
            self.order_place_url,
            json.dumps(data, cls=UUIDEncoder),
            content_type="application/json"
        )

        self.client.post(
            self.order_place_url,
            json.dumps(data, cls=UUIDEncoder),
            content_type="application/json"
        )

        orders = Order.objects.all()

        response = self.client.get(self.order_list_url)

        print('\n\nresponse.json(): {}\n\n'.format(response.json()))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()['count'], orders.count())


    def test_order_place_view_POST(self):

        data = create_post_data(self.restaurant, self.item, self.item_type)

        response = self.client.post(
            self.order_place_url, 
            json.dumps(data, cls=UUIDEncoder),
            content_type="application/json"
        )

        print('\n\n\nRESPONSE: {}\n\n\n'.format(response.json()))

        self.assertEquals(response.status_code, 201)

        expected_response = {'Success': 'Order successfully created'}

        self.assertJSONEqual(response.content, json.dumps(expected_response))

        order = Order.objects.all().first()

        self.assertEqual(order.total_price, self.item_type.price)

        self.assertEqual(order.footnote, data['footnote'])
