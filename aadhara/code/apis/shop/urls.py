from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/', views.AddToCart.as_view(),name="addtocartapi"),
 	path('create-order/', views.CreateOrder.as_view(),name="createorderapi"),
 	path('update-order-payment/', views.UpdateOrderPayment.as_view(),name="updateorderpaymentapi"),
	path('wishlist/', views.WishlistAPIView.as_view(),name="wishlistapi"),
	path('checkserviceability/', views.Checkserviceability.as_view(),name="checkserviceability"),      
]
