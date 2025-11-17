from django.urls import path
from . import views

urlpatterns = [
    # The homepage will be the authentication page
    path('', views.get_token_view, name='get_token'), 

    path('devices/', views.device_list_view, name='device_list'),
    path('interfaces/', views.interface_list_view, name='interface_list'),
    path('logs/', views.logs_view, name='logs'),
]
