from django.db import models
from django.contrib.gis.db import models as gis_models

from core.models import BaseModel, Rating, GeoPoint

from user.models import User

from merchant.models import Restaurant, MenuItem
from order.managers import OrderManager


class Order(BaseModel):

    class STATUS:
        SENT = "SENT"
        CANCELLED = "CANCELLED"
        REFUSED = "REFUSED"
        ACCEPTED = "ACCEPTED"
        DELIVERED = "DELIVERED"

        CHOICES = (
            (SENT, "sent"),
            (CANCELLED, "cancelled"),
            (REFUSED, "refused"),
            (ACCEPTED, "accepted"),
            (DELIVERED, "delivered"),
        )

    restaurant = models.ForeignKey(Restaurant, related_name='orders', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)

    footnote = models.CharField(max_length=400)

    visible = models.BooleanField(default=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_responded = models.DateTimeField(auto_now=True)

    manager = OrderManager()

    gis_delivery_point = gis_models.PointField()

    # won't be used right now but we will need it
    date_delivered = models.DateTimeField(null=True, blank=True, default=None)

    status = models.CharField(max_length=10, choices=STATUS.CHOICES, default=STATUS.SENT)

    @property
    def delivery_point(self):
        return {
            'latitude': self.gis_delivery_point.y,
            'longitude': self.gis_delivery_point.x
        }

    @property
    def total_delivery_time_min(self):
        return self.items.earliest('delivery_time_min').delivery_time_min

    @property
    def total_delivery_time_max(self):
        return self.items.latest('delivery_time_max').delivery_time_max

    @property
    def total_price(self):
        total_price = 0

        for item in self.items.all():
            total_price += item.total_price

        return total_price

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'User Order'
        verbose_name_plural = 'User Orders'

    def __str__(self):
        # return 'Order ID ' + str(self.id) + \
               # ' at lat:' + str(self.delivery_point.latitude) + ' long:' + str(self.delivery_point.longitude)
        return 'Order ID ' + str(self.id)


class ServiceRating(Rating):
    user = models.ForeignKey(User, related_name='order_ratings', on_delete=models.CASCADE)
    order = models.OneToOneField(Order, related_name='rating', on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name = 'Order Delivery Service Rating'
        verbose_name_plural = 'Order Delivery Service Ratings'


class OrderMenuItem(BaseModel):
    count = models.IntegerField()

    delivery_time_min = models.IntegerField()
    delivery_time_max = models.IntegerField()

    related_item = models.ForeignKey(MenuItem, related_name='ordered_items', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)

    @property
    def total_price(self):
        total_price = self.type.price

        for option in self.options.all():
            if option.price:
                total_price += option.price

        return self.count * total_price

    class Meta:
        verbose_name = 'User Order Menu Item'
        verbose_name_plural = 'User Order Menu Items'

    def __str__(self):
        return 'Order: ' + str(self.order.pk) + ' : ' + self.related_item.name


class OrderMenuItemType(BaseModel):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    order_item = models.OneToOneField(OrderMenuItem, related_name='type', on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.name


class OrderMenuItemOption(BaseModel):
    name = models.CharField(max_length=100)
    price = models.FloatField(null=True, blank=True)

    order_item = models.ForeignKey(OrderMenuItem, related_name='options', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
