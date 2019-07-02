from django.urls import path
from merchant import views

app_name = 'merchant'

urlpatterns = [
    path(r'search', views.AvailableRestaurantsListView.as_view(), name='search'),
    path(r'available', views.RestaurantAvailabilityCheck.as_view(), name='available'),
    path(r'<uuid:restaurant_uuid>', views.RestaurantView.as_view(), name='detail'),
    path(r'item/<uuid:menu_item_uuid>', views.MenuItemView.as_view(), name='item'),
    path(r'category/', views.CategoryListView.as_view(), name='categories'),
    path(r'category/<uuid:category_uuid>', views.CategoryView.as_view(), name='category'),
]
