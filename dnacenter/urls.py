from django.urls import path
from . import views

app_name = 'dnacenter'

urlpatterns = [
    path('', views.index, name='index'),
    path('authenticate/', views.authenticate, name='authenticate'),
    path('devices/', views.list_devices, name='list_devices'),
    path('interfaces/', views.device_interfaces, name='device_interfaces'),
]