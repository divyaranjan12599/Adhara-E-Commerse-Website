from django.urls import path,include
from . import views

app_name = 'shop'
urlpatterns = [
    path('product/<slug>-<int:product_id>-detail', views.ProductDetailView.as_view(),name="productdetail"),

    path('cart', views.CartView.as_view(),name="cart"),
    path('checkout', views.CheckoutView.as_view(),name="checkout"),
    path('order-placed', views.OrderPlacedView.as_view(),name="orderplaced"),
    path('order-retry-<order_id>', views.OrderRetryPaymentView.as_view(),name="paymentretry"),
    path('<slug>--<id>', views.ProductListView.as_view(), name="productlist"),
    path('admin/', include('shop.admin_urls')),
]
