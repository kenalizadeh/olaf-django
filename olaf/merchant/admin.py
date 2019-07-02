from django.contrib import admin
from merchant.models import *
from leaflet.admin import LeafletGeoAdmin


admin.site.register(RestaurantRating)
admin.site.register(MenuItemOption)
admin.site.register(MenuItemType)
admin.site.register(MenuItemCategory)


class MenuItemTypeInline(admin.StackedInline):
    exclude = ('is_deleted', 'date_deleted')
    model = MenuItemType
    extra = 0


class MenuItemOptionInline(admin.StackedInline):
    exclude = ('is_deleted', 'date_deleted')
    model = MenuItemOption
    extra = 0


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    exclude = ('is_deleted', 'date_deleted')
    list_display = ['id', 'name', 'restaurant', 'category', 'base_price', 'active', 'recommended']
    list_display_links = ['id', 'name']

    def base_price(self, obj):
        return "AZN {0}".format(obj.base_price)

    inlines = [
        MenuItemOptionInline,
        MenuItemTypeInline,
    ]

    def get_queryset(self, request):
        # use our manager, rather than the default one
        qs = self.model.objects.get_queryset()

        # we need this from the superclass method
        ordering = self.ordering or ()  # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(Restaurant)
class RestaurantAdmin(LeafletGeoAdmin):
    exclude = ('is_deleted', 'date_deleted')
    readonly_fields = ('date_joined', 'uuid')

    list_filter = (
        'date_joined',
    )

    list_display = (
        'title',
        'description',
        'date_joined',
        'recommended_items_count'
    )

    def recommended_items_count(self, obj):
        return "{0} item(s)".format(obj.recommended_items.count())
