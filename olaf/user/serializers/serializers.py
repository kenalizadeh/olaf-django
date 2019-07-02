from rest_framework import serializers

from user.models import *


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        exclude = ('user',)


class FootNoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootNote
        fields = '__all__'


class FootNoteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootNote
        fields = ('id', 'name', 'message')


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.ReadOnlyField()

    class Meta(object):
        model = User
        fields = ('date_joined', 'phone_number')
        extra_kwargs = {'password': {'write_only': True}}


class UserProfileSerializer(serializers.ModelSerializer):

    total_order_count = serializers.SerializerMethodField()
    total_order_amount = serializers.SerializerMethodField()

    class Meta(object):
        model = UserProfile
        fields = (
            'first_name',
            'last_name',
            'email_address',
            'preferred_language',
            'subscribed_to_email',
            'total_order_count',
            'total_order_amount'
        )

    def get_total_order_count(self, obj):
        return obj.total_order_count

    def get_total_order_amount(self, obj):
        return obj.total_order_amount


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(many=False)
    date_joined = serializers.DateTimeField(format="%d-%m-%Y %H:%M")

    class Meta(object):
        model = User
        fields = ('phone_number', 'date_joined', 'profile')


class UserProfileUpdateSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = UserProfile
        fields = ('email_address', 'first_name', 'last_name')
