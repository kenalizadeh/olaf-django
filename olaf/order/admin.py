from django.contrib import admin
from order.models import *

from leaflet.admin import LeafletGeoAdmin


admin.site.register(ServiceRating)


class OrderMenuItemTypeInline(admin.TabularInline):
    model = OrderMenuItemType
    extra = 1
    can_delete = False


class OrderMenuItemOptionInline(admin.TabularInline):
    model = OrderMenuItemOption
    extra = 1
    can_delete = False


@admin.register(OrderMenuItem)
class OrderMenuItemAdmin(admin.ModelAdmin):
    inlines = [
        OrderMenuItemOptionInline,
        OrderMenuItemTypeInline
    ]


class OrderMenuItemInline(admin.TabularInline):
    model = OrderMenuItem
    readonly_fields = ('count', 'delivery_time', 'related_item', 'total_price')
    fields = readonly_fields
    extra = 0
    can_delete = False
    show_change_link = True

    def delivery_time(self, obj):
        return str(obj.delivery_time_min) + '/' + str(obj.delivery_time_max) + ' mins.'


@admin.register(Order)
class UserOrderAdmin(LeafletGeoAdmin):

    list_display = (
        'id',
        'footnote',
        'delivery_location',
        'restaurant',
        'user',
        'item_count',
        'total_price',
        'date_created',
        'date_delivered',
        'status',
        'visible'
    )

    list_display_links = ('id', 'footnote', 'delivery_location')

    readonly_fields = (
        'visible',
        'restaurant',
        'user',
        'total_price',
        'footnote',
        'status',
        'date_created',
        'date_delivered',
        'date_responded'
    )

    fields = (
        'visible',
        'restaurant',
        'user',
        'total_price',
        'footnote',
        'status',
        'gis_delivery_point',
        'date_created',
        'date_delivered',
        'date_responded'
    )

    inlines = [
        OrderMenuItemInline
    ]

    def total_price(self, obj):
        return "AZN {0}".format(obj.total_price)

    def item_count(self, obj):
        return "{0} item(s)".format(obj.items.all().count())

    def delivery_location(self, obj):
        return str(obj.delivery_point['latitude']) + ', ' + str(obj.delivery_point['longitude'])
