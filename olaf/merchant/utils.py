from merchant.models import Restaurant

from math import sin, cos, sqrt, atan2
from math import radians as rad


def filter_available_restaurants_queryset(user):

    user_lat = user.activity.latitude
    user_long = user.activity.longitude

    restaurants = Restaurant.objects.all()

    # Haversine formula for calculating the distance.
    # Altitude is not calculated

    r = 6373.0
    lat1 = rad(user_lat)
    lon1 = rad(user_long)

    restaurants_dict = {}

    for restaurant in restaurants:
        lat2 = rad(restaurant.location.latitude)
        lon2 = rad(restaurant.location.longitude)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # distance in meters
        distance = r * c * 1000

        if distance <= restaurant.delivery_range or restaurant.delivery_range <= 0:
            restaurants_dict[restaurant.id] = distance

    filtered_restaurants = restaurants.filter(id__in=restaurants_dict.keys())

    for filtered_restaurant in filtered_restaurants:
        filtered_restaurant.distance = restaurants_dict[filtered_restaurant.id]

    filtered_restaurants.order_by('-listing_priority')

    # serializer = RestaurantSerializerForFeed(filtered_restaurants, many=True, context={'request': request})

    return filtered_restaurants
