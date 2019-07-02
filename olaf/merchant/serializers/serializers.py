from rest_framework import serializers

from merchant.models import *


class UserRestaurantRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantRating
        fields = '__all__'


class RatingSerializerForRestaurant(serializers.ModelSerializer):
    class Meta:
        model = RestaurantRating
        exclude = ('restaurant',)


class RatingSerializerForUser(serializers.ModelSerializer):
    class Meta:
        model = RestaurantRating
        exclude = ('user',)


class MenuItemCategoryBasicSerializer(serializers.ModelSerializer):
    items_count = serializers.ReadOnlyField()

    class Meta:
        model = MenuItemCategory
        fields = ('uuid', 'name', 'image', 'items_count')


class MenuItemTypeSerializer(serializers.ModelSerializer):
    menu_item = serializers.UUIDField(source='menu_item.uuid')

    class Meta:
        model = MenuItemType
        fields = ('uuid', 'name', 'price', 'state', 'menu_item')


class MenuItemOptionsSerializer(serializers.ModelSerializer):
    menu_item = serializers.UUIDField(source='menu_item.uuid')

    class Meta:
        model = MenuItemOption
        fields = ('uuid', 'name', 'price', 'state', 'menu_item')


class MenuItemShortSerializer(serializers.ModelSerializer):
    base_price = serializers.ReadOnlyField()

    class Meta:
        model = MenuItem
        fields = ('uuid', 'name', 'description', 'image', 'base_price', 'delivery_time_min', 'delivery_time_max')


class RestaurantSerializerForFeed(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField(read_only=True)
    recommended_items = MenuItemShortSerializer(many=True, read_only=True)

    def get_distance(self, obj):
        return obj.distance.m

    class Meta:
        model = Restaurant
        fields = ('uuid', 'title', 'description', 'image', 'distance', 'location', 'recommended_items')


class RestaurantDetailShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('uuid', 'title', 'image')


class MenuItemSerializer(serializers.ModelSerializer):
    restaurant = RestaurantDetailShortSerializer(many=False, read_only=True)
    options = MenuItemOptionsSerializer(many=True, read_only=True)
    types = MenuItemTypeSerializer(many=True, read_only=True)
    category = MenuItemCategoryBasicSerializer(many=False, read_only=True)
    base_price = serializers.ReadOnlyField()

    class Meta:
        model = MenuItem
        fields = (
            'restaurant',
            'uuid',
            'name',
            'description',
            'recommended',
            'image',
            'category',
            'types',
            'options',
            'base_price',
            'delivery_time_min',
            'delivery_time_max')


class RestaurantDetailSerializer(serializers.ModelSerializer):
    menu_items = MenuItemShortSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ('uuid', 'title', 'description', 'image', 'location', 'menu_items')


class MenuItemCategorySerializer(serializers.ModelSerializer):
    menu_items = MenuItemShortSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItemCategory
        fields = ('uuid', 'name', 'image', 'menu_items')
