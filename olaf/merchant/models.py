from django.db import models
from django.contrib.gis.db import models as gis_models

from core.models import BaseModel, Rating, GeoPoint

from merchant import managers
from user.models import User


class MerchantBrand(BaseModel):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    logo = models.ImageField(upload_to='brand/')

    def __str__(self):
        return self.name


class Restaurant(BaseModel):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=400, blank=True, default='')
    image = models.ImageField(upload_to='merchant/')

    delivery_area = gis_models.MultiPolygonField()
    gis_location = gis_models.PointField()

    # Not sure we need this now
    date_joined = models.DateTimeField(auto_now_add=True)

    managers = models.ManyToManyField(User, related_name='restaurants')
    brand = models.ForeignKey(MerchantBrand, related_name='restaurants', on_delete=models.DO_NOTHING, null=True, blank=True)

    @property
    def location(self):
        return {
            'latitude': self.gis_location.y,
            'longitude': self.gis_location.x
        }

    @property
    def recommended_items(self):
        return self.menu_items(manager='recommended_objects').all()

    def __str__(self):
        return self.title


class RestaurantRating(Rating):
    user = models.ForeignKey(User, related_name='restaurant_ratings', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name='ratings', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Restaurant Rating'
        verbose_name_plural = 'Restaurant Ratings'


class MenuItemCategory(BaseModel):
    name = models.CharField(max_length=20, unique=True)
    image = models.ImageField(upload_to='category/')

    @property
    def items_count(self):
        return self.menu_items(manager='active_objects').all().count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Menu Item Category'
        verbose_name_plural = 'Menu Item Categories'


class MenuItem(BaseModel):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=400, default='', blank=True)
    recommended = models.BooleanField(default=False)
    listing_priority = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='fullsize/')

    # Delivery times in minutes
    delivery_time_min = models.IntegerField()
    delivery_time_max = models.IntegerField()

    restaurant = models.ForeignKey(Restaurant, related_name='menu_items', on_delete=models.CASCADE)
    category = models.ForeignKey(MenuItemCategory, related_name='menu_items', on_delete=models.CASCADE)

    active_objects = managers.MenuItemManager()
    recommended_objects = managers.RecommendedMenuItemManager()

    @property
    def base_price(self):
        return self.types.get(state=True).price

    class Meta:
        verbose_name = 'Restaurant Menu Item'
        verbose_name_plural = 'Restaurant Menu Items'

    def __str__(self):
        return self.name + ' : ' + self.restaurant.title


class MenuItemOption(BaseModel):
    name = models.CharField(max_length=100)
    state = models.BooleanField(default=False)
    price = models.FloatField(null=True, blank=True)

    menu_item = models.ForeignKey(MenuItem, related_name='options', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Restaurant Menu Item Option'
        verbose_name_plural = 'Restaurant Menu Item Options'

    def __str__(self):
        return self.name


class MenuItemType(BaseModel):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    state = models.BooleanField()

    menu_item = models.ForeignKey(MenuItem, related_name='types', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Restaurant Menu Item Type'
        verbose_name_plural = 'Restaurant Menu Item Types'

    def __str__(self):
        return self.name + ' : ' + self.menu_item.name
