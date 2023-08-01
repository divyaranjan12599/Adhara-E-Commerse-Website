from django.urls import path
from . import views
urlpatterns = [
    path('nimbuspost/create_order/', views.CreateOrder.as_view(),name="nimbuspost_create_order"),
    path('request_pickup/', views.RequestPickup.as_view(),name="nimbuspost_request_pickup"),
    path('truck_order_status/', views.TruckOrderStatus.as_view(),name="nimbuspost_track_order_status"),
]