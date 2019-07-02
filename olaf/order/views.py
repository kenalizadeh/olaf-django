from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from core.paginators import DefaultPagination
from order.serializers.serializers import *
from merchant.models import *
from core.serializers.serializers import *
from olaf.tasks import handle_order
from django.utils import timezone
from core.forms import GeoPointForm

from django.contrib.gis import geos

import logging

import datetime


logger = logging.getLogger(__name__)


class OrdersListView(ListAPIView):

    model_class = Order
    serializer_class = OrderDetailSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):

        visibility = self.request.GET.get('new', True)

        return self.model_class.objects.filter(user=self.request.user, visible=visibility)

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        serializer = self.serializer_class(queryset, many=True, context={'request': self.request})

        page = self.paginate_queryset(serializer.data)

        return self.get_paginated_response(page)


class OrderCreateView(APIView):

    serializer_class = OrderSerializer

    def post(self, request):
        if not request.data.get('items'):
            return Response({'BadRequest': 'items required'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.data.get('delivery_point'):
            return Response({'BadRequest': 'delivery_point required'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.data.get('restaurant'):
            return Response({'BadRequest': 'restaurant required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            restaurant = Restaurant.objects.get(uuid=request.data.get('restaurant'))
        except Restaurant.DoesNotExist:
            return Response({'BadRequest': 'restaurant does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['user'] = request.user.pk
        data['restaurant'] = restaurant.pk

        delivery_point_form = GeoPointForm(data['delivery_point'])

        if not delivery_point_form.is_valid():
            return Response(delivery_point_form.errors, status=status.HTTP_400_BAD_REQUEST)

        latitude = float(delivery_point_form.cleaned_data['latitude'])
        longitude = float(delivery_point_form.cleaned_data['longitude'])

        delivery_point = geos.Point(longitude, latitude)

        order_serializer = self.serializer_class(data=data)
        order_serializer.is_valid(raise_exception=True)
        order_instance = order_serializer.save(gis_delivery_point=delivery_point)

        items = data.get('items')
        for item in items:
            item_id = item.get('id')
            item_count = item.get('count')
            selected_type = item.get('type')

            if not item_id or not item_count or not selected_type:
                order_instance.delete()
                res = {'BadRequest': 'item id, item count, item type required'}
                return Response(res, status=status.HTTP_400_BAD_REQUEST)

            try:
                menu_item = MenuItem.objects.get(uuid=item_id, restaurant=order_instance.restaurant)
            except MenuItem.DoesNotExist:
                order_instance.delete()
                return Response({'BadRequest': 'item does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            order_menu_item = OrderMenuItem()
            order_menu_item.count = item_count
            order_menu_item.delivery_time_min = menu_item.delivery_time_min
            order_menu_item.delivery_time_max = menu_item.delivery_time_max
            order_menu_item.related_item = menu_item
            order_menu_item.order = order_instance
            order_menu_item.save()

            options = item.get('options')
            if options:
                for option in options:
                    try:
                        menu_item_option = MenuItemOption.objects.get(uuid=option, menu_item=menu_item.pk)
                    except MenuItemOption.DoesNotExist:
                        order_instance.delete()
                        return Response({'Error', 'option does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                    order_menu_item_option = OrderMenuItemOption()
                    order_menu_item_option.name = menu_item_option.name
                    order_menu_item_option.price = menu_item_option.price
                    order_menu_item_option.order_item = order_menu_item
                    order_menu_item_option.save()

            try:
                menu_item_type = MenuItemType.objects.get(uuid=selected_type, menu_item=menu_item.pk)
            except MenuItemType.DoesNotExist:
                order_instance.delete()
                return Response({'Error', 'type does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            order_menu_item_type = OrderMenuItemType()
            order_menu_item_type.name = menu_item_type.name
            order_menu_item_type.price = menu_item_type.price
            order_menu_item_type.order_item = order_menu_item
            order_menu_item_type.save()

        handle_order.apply_async((order_instance.pk,), eta=timezone.now() + datetime.timedelta(minutes=10))
        res = {'Success': 'Order successfully created'}
        return Response(res, status=status.HTTP_201_CREATED)


class OrderView(APIView):

    model_class = Order
    serializer_class = OrderDetailSerializer

    def get(self, request, order_id):

        try:
            order = self.model_class.objects.get(pk=order_id, user=request.user, visible=True)

            serializer = self.serializer_class(order, many=False, context={'request': request})
        except self.model_class.DoesNotExist:
            return Response({'Error': 'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, order_id):

        try:
            order = self.model_class.objects.get(pk=order_id, user=request.user, visible=True)
            order.visible = False
            order.save()

            serializer = self.serializer_class(order, many=False, context={'request': request})

        except self.model_class.DoesNotExist:
            return Response({'Error': 'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, order_id):

        try:
            order = self.model_class.objects.get(pk=order_id, user=request.user, visible=True)
            if order.status == self.model_class.SENT:
                order.status = self.model_class.CANCELLED
                order.save()

                serializer = self.serializer_class(order, many=False, context={'request': request})

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'Error': 'Order status has already changed'}, status=status.HTTP_400_BAD_REQUEST)

        except self.model_class.DoesNotExist:
            return Response({'Error': 'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)


class MerchantOrdersView(APIView):

    def get(self, request, restaurant_uuid, *args, **kwargs):

        if not request.user.is_business:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            restaurant = request.user.restaurants.get(uuid=restaurant_uuid)
        except Restaurant.DoesNotExist:
            return Response({'BadRequest': 'restaurant does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        orders = restaurant.orders.pending()

        serializer = OrderDetailSerializer(orders, many=True, context={'request': request})

        return Response(serializer.data, status.HTTP_200_OK)
