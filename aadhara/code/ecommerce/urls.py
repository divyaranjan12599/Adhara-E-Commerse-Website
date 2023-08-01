"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from argparse import Namespace
from os import name
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from core.views import static_pages,ProductSitemap
from shop.views import SearchView
from users.views import logout
from users.views import Error404View
handler404 = Error404View.as_view()

from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'core':ProductSitemap
    
}



urlpatterns = [
    path('manage-admin/', admin.site.urls),
    path('shop/', include('shop.urls')),
    path('shop_admin/', include('shop_admin.urls')),
    path('shop_admin_old/', include('shop.admin_urls')),
    path('user/', include('users.urls')),
    path('api/v1/', include('apis.urls')),
    path('pages/<static_page>', static_pages, name='static_page'),
    path('blog/', include('blogs.urls')),
    path('',include('core.urls')),
    path('search', SearchView.as_view(), name='search'),
    path('logout/', logout, name='logout'),

    path('sitemap.xml',sitemap,{'sitemaps':sitemaps},name='sitemap')

    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)