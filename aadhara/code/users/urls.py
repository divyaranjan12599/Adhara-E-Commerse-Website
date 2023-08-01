from django.urls import path
from . import views
from django.urls import reverse_lazy


app_name = 'users'
urlpatterns = [
    path('register.html', views.RegisterView.as_view(),name="register"),
    path('account.html', views.MyAccountView.as_view(),name="account"),
    path('wishlist.html', views.WishlistView.as_view(),name="wishlist"),        
    
    path('edit-profile.html', views.EditProfileView.as_view(),name="editprofile"),
    path('change-password.html', views.ChangePasswordView.as_view(),name="changepassword"),
    path('reset-password.html', views.ChangePasswordView.as_view(),name="resetpassword"),
        
    path('my-addresses.html', views.MyAddressesView.as_view(),name="myaddresses"),
    path('update-address.html', views.AddressAddEditView.as_view(),name="updateaddress"),
    path('orders.html', views.MyOrdersView.as_view(),name="orders"),
    path('order-details.html', views.OrderDetailsView.as_view(),name="orderdetails"),
    path('invoice.html', views.InvoiceView.as_view(),name="invoice"),
    
    path('login.html', views.LoginView.as_view(),name="login"),
    path('forgot-password.html', views.ForgotPasswordView.as_view(success_url='/'),name="forgotpassword"),
    path('password-reset-confirm/<uidb64>/<token>/',views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'), 

]
