from django.test import TestCase, Client
from django.shortcuts import reverse
from django.db.models import signals
from django.contrib.auth import get_user_model

from django.contrib.gis import geos

import uuid
import json

from user.models import User, UserActivity
from merchant.models import (
        Restaurant,
        MenuItem,
        MenuItemType,
        MenuItemCategory
    )


def generate_polygon(latitude, longitude, radius):
    center = geos.Point(longitude, latitude)
    circle = center.buffer(radius)

    return geos.MultiPolygon(geos.fromstr(str(circle)),)


class MerchantSearchTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(phone_number='994508874380', password='12345')

        latitude = 40.402105
        longitude = 49.868889

        UserActivity.objects.create(user=self.user, gis_location=geos.Point(longitude, latitude))

        self.restaurant = Restaurant.objects.create(
            title='Restaurant 1',
            description='Restaurant 1',
            gis_location=geos.Point(longitude, latitude),
            delivery_area=generate_polygon(latitude, longitude, 0.009)
        )

    def test_restaurant_filter(self):

        yasamal_lat = 40.382643
        yasamal_long = 49.809322

        user_point = geos.Point(49.868976, 40.402100)

        restaurants = Restaurant.objects.filter(delivery_area__contains=user_point)
        print('\n\nrestaurants: {}\n\n'.format(restaurants))

        self.assertEqual(restaurants.exists(), True)

        user_point = geos.Point(yasamal_long, yasamal_lat)

        restaurants = Restaurant.objects.filter(delivery_area__contains=user_point)
        print('\n\nrestaurants: {}\n\n'.format(restaurants))

        self.assertEqual(restaurants.exists(), False)



class MerchantAPIResponseTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(phone_number='994508874380', password='12345')

        latitude = 40.402105
        longitude = 49.868889

        UserActivity.objects.create(user=self.user, gis_location=geos.Point(longitude, latitude))

        self.client.login(phone_number='994508874380', password='12345')

        self.rest1 = Restaurant.objects.create(
            title='Restaurant 1',
            description='Restaurant 1',
            gis_location=geos.Point(longitude, latitude),
            delivery_area=generate_polygon(latitude, longitude, 0.009)
        )

        self.rest2 = Restaurant.objects.create(
            title='Restaurant 2',
            description='Restaurant 2',
            gis_location=geos.Point(longitude, latitude),
            delivery_area=generate_polygon(latitude, longitude, 0.009)
        )

        self.rest3 = Restaurant.objects.create(
            title='Restaurant 3',
            description='Restaurant 3',
            gis_location=geos.Point(longitude, latitude),
            delivery_area=generate_polygon(latitude, longitude, 0.009)
        )

        self.available_restaurant_list_view_url_GET = reverse('merchant:search')

    def test_available_restaurant_list_view_GET(self):

        response = self.client.get(self.available_restaurant_list_view_url_GET)

        self.assertEquals(response.status_code, 200)

        self.assertEqual(response.json()["count"], 3)

    def test_restaurant_detail_view_GET(self):

        restaurant_detail_view_url_GET = reverse('merchant:detail', kwargs={'restaurant_uuid': self.rest1.uuid})

        response = self.client.get(restaurant_detail_view_url_GET)

        self.assertEquals(response.status_code, 200)

        restaurant_detail_view_url_GET = reverse('merchant:detail', kwargs={'restaurant_uuid': uuid.uuid4()})

        response = self.client.get(restaurant_detail_view_url_GET)

        self.assertEqual(response.status_code, 404)
