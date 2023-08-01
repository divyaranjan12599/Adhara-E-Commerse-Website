from django.urls import path
from . import views
urlpatterns = [
    path('create_order/', views.CreateOrder.as_view(),name="shiprocket_create_order"),
    path('generate_awb/', views.GenerateAWB.as_view(),name="shiprocket_generate_awb"),
    path('request_pickup/', views.RequestPickup.as_view(),name="shiprocket_request_pickup"),

]
