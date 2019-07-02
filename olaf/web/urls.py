from django.urls import path
from web import views

app_name = 'web'

urlpatterns = [
    path(r'', views.IndexView.as_view(), name='index')
]
