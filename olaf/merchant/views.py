from django.shortcuts import render

from django.contrib.gis import geos
from django.contrib.gis.db.models.functions import Distance

from merchant.models import *
from merchant.serializers.serializers import *

# from merchant.utils import filter_available_restaurants_queryset
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from core.paginators import DefaultPagination
from core.forms import GeoPointForm

import logging

logger = logging.getLogger(__name__)


class AvailableRestaurantsListView(ListAPIView):

    serializer_class = RestaurantSerializerForFeed
    pagination_class = DefaultPagination

    def get_queryset(self, user_location):

        restaurants = Restaurant.objects.filter(delivery_area__contains=user_location)\
        .annotate(distance=Distance('gis_location', user_location))\
        .order_by('-distance')

        return restaurants

    def get(self, *args, **kwargs):

        form = GeoPointForm(self.request.GET)

        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        latitude = float(form.cleaned_data['latitude'])
        longitude = float(form.cleaned_data['longitude'])

        user_location = geos.Point(longitude, latitude)

        serializer = self.serializer_class(self.get_queryset(user_location), many=True, context={'request': self.request})

        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class RestaurantAvailabilityCheck(APIView):

    def get(self, request, *args, **kwargs):

        form = GeoPointForm(request.GET)

        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        latitude = float(form.cleaned_data['latitude'])
        longitude = float(form.cleaned_data['longitude'])

        user_location = geos.Point(longitude, latitude)

        restaurants_count = Restaurant.objects.filter(delivery_area__contains=user_location).count()

        return Response({'count': restaurants_count}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        form = GeoPointForm(request.data)

        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        latitude = float(form.cleaned_data['latitude'])
        longitude = float(form.cleaned_data['longitude'])

        user_location = geos.Point(longitude, latitude)

        restaurants_count = Restaurant.objects.filter(delivery_area__contains=user_location).count()

        return Response({'count': restaurants_count}, status=status.HTTP_200_OK)


class RestaurantView(APIView):

    def get(self, request, restaurant_uuid):

        try:
            restaurant = Restaurant.objects.get(uuid=restaurant_uuid)

            serializer = RestaurantDetailSerializer(restaurant, many=False, context={'request': request})
        except Restaurant.DoesNotExist:
            return Response({'Error': 'Restaurant does not exist'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MenuItemView(APIView):

    def get(self, request, menu_item_uuid):

        try:
            item = MenuItem.active_objects.get(uuid=menu_item_uuid)

            serializer = MenuItemSerializer(item, many=False, context={'request': request})
        except MenuItem.DoesNotExist:
            return Response({'Error': 'MenuItem does not exist'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryListView(ListAPIView):

    model_class = MenuItemCategory
    serializer_class = MenuItemCategoryBasicSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        return self.model_class.objects.all()

    def get(self, *args, **kwargs):

        serializer = self.serializer_class(self.get_queryset(), many=True, context={'request': self.request})

        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class CategoryView(APIView):

    def get(self, request, category_uuid):

        try:
            category = MenuItemCategory.objects.get(uuid=category_uuid)
        except MenuItemCategory.DoesNotExist:
            return Response({'Error': 'Category does not exist'}, status.HTTP_404_NOT_FOUND)

        serializer = MenuItemCategorySerializer(category, many=False, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


def filter_restaurants(request):

    search_param = request.data.get("filter")

    restaurants = Restaurant.objects.filter(title__icontains=search_param)

    serializer = RestaurantDetailSerializer(restaurants, many=True, context={'request': request})

    return Response(serializer.data, status=status.HTTP_200_OK)
