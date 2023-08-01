from django.contrib import admin
from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.homepage,name='homepage'),
    path('subscribe',views.subscribe,name='subscribe'),
    path('contact_us', views.contact_us,name="contactus"),
    path('gallery',views.gallery_view,name='gallery'),



]