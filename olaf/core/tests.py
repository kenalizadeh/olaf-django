from django.test import TestCase

from core.models import BaseModel
from merchant.models import (
    Restaurant,
    RestaurantLocation
)


class BaseModelTests(TestCase):

    def setUp(self):

        latitude = 40.402105
        longitude = 49.868889

        self.restaurant = Restaurant.objects.create(title='Restaurant 1', description='Restaurant 1', delivery_range=0)
        RestaurantLocation.objects.create(restaurant=self.restaurant, latitude=latitude, longitude=longitude)

    def test_base_model_soft_delete_status(self):

        self.assertFalse(self.restaurant.is_deleted)

        self.restaurant.delete()

        self.assertTrue(self.restaurant.is_deleted)

    def test_base_model_soft_delete_accessibility(self):

        self.restaurant.delete()

        try:
            restaurant_get = Restaurant.objects.get(uuid=self.restaurant.uuid)
        except Restaurant.DoesNotExist:
            restaurant_get = None

        self.assertIsNone(restaurant_get)

        try:
            restaurant_get = Restaurant.objects_including_deleted.get(uuid=self.restaurant.uuid)
        except Restaurant.DoesNotExist:
            restaurant_get = None

        self.assertIsNotNone(restaurant_get)

    def test_base_model_soft_delete_restore(self):

        self.restaurant.delete()
        self.restaurant.restore()

        try:
            restaurant_get = Restaurant.objects.get(uuid=self.restaurant.uuid)
        except Restaurant.DoesNotExist:
            restaurant_get = None

        self.assertIsNotNone(restaurant_get)

    def test_base_model_soft_delete_erase(self):

        try:
            restaurant_get = Restaurant.objects.get(uuid=self.restaurant.uuid)
        except Restaurant.DoesNotExist:
            restaurant_get = None

        self.assertIsNotNone(restaurant_get)

        self.restaurant.erase()

        try:
            restaurant_get = Restaurant.objects.get(uuid=self.restaurant.uuid)
        except Restaurant.DoesNotExist:
            restaurant_get = None

        self.assertIsNone(restaurant_get)
