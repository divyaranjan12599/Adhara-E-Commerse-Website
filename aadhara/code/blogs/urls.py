from django.contrib import admin
from django.urls import path
from . import views

app_name = 'blogs'
urlpatterns = [
    path('detail/<int:id>',views.blog_detail_view,name='blog_detail'),
    path('all',views.blog_view,name='bloglist'),
    
]