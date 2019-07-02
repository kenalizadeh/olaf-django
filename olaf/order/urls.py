from django.urls import path
from order import views


app_name = 'order'

urlpatterns = [
    path(r'list', views.OrdersListView.as_view(), name='list'),
    path(r'list/<uuid:restaurant_uuid>', views.MerchantOrdersView.as_view(), name='merchant-orders'),
    path(r'place', views.OrderCreateView.as_view(), name='create'),
    path(r'<int:order_id>', views.OrderView.as_view(), name='detail')
]
