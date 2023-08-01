from django.urls import path, include
import users.views as user_views
app_name = 'api'

urlpatterns = [
    path('user/', include('apis.user.urls')),
    path('utils/', include('apis.utils.urls')),
    path('shop/', include('apis.shop.urls')),
    path('shiprocket/', include('apis.shiprocket.urls')),
    path('nimbuspost/', include('apis.nimbuspost.urls')),
]
