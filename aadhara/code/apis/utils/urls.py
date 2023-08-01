from django.urls import path
from . import views

urlpatterns = [
    path('cs-by-pincode/', views.CityStateByPin.as_view(),name="csbypincode"),
]
