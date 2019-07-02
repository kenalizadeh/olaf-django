from rest_framework import serializers

from order.models import *

from merchant.serializers.serializers import MenuItemCategoryBasicSerializer


class OrderRestaurantShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('uuid', 'title', 'image')


class RelatedMenuItemShortSerializer(serializers.ModelSerializer):
    category = MenuItemCategoryBasicSerializer(many=False, read_only=False)

    class Meta:
        model = MenuItem
        fields = ('uuid', 'name', 'description', 'category', 'image')


class OrderMenuItemOptionsSerializer(serializers.ModelSerializer):
    order_item = serializers.UUIDField(source='order_item.uuid')

    class Meta:
        model = OrderMenuItemOption
        fields = ('order_item', 'uuid', 'name', 'price')


class OrderMenuItemTypeSerializer(serializers.ModelSerializer):
    order_item = serializers.UUIDField(source='order_item.uuid')

    class Meta:
        model = OrderMenuItemType
        fields = ('order_item', 'uuid', 'name', 'price')


class OrderMenuItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderMenuItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        exclude = ('gis_delivery_point', )
        # fields = '__all__'


class OrderMenuItemDetailSerializer(serializers.ModelSerializer):
    type = OrderMenuItemTypeSerializer(many=False)
    options = OrderMenuItemOptionsSerializer(many=True)
    related_item = RelatedMenuItemShortSerializer(many=False, read_only=True)

    class Meta:
        model = OrderMenuItem
        fields = ('uuid', 'related_item', 'count', 'delivery_time_min', 'delivery_time_max', 'type', 'options')


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderMenuItemDetailSerializer(many=True)
    delivery_point = serializers.DictField()
    total_delivery_time_min = serializers.ReadOnlyField()
    total_delivery_time_max = serializers.ReadOnlyField()
    restaurant = OrderRestaurantShortSerializer(many=False, read_only=True)

    date_created = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    date_responded = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    date_delivered = serializers.DateTimeField(format="%d-%m-%Y %H:%M")

    class Meta:
        model = Order
        exclude = ('id', 'visible', 'user', 'is_deleted', 'date_deleted')
