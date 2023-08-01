from django.urls import path
from . import views

urlpatterns = [
    path('send-otp/', views.SendOTP.as_view(),name="sendotp"),
    path('verify-otp/', views.VerifyOTP.as_view(),name="verifyotp"),
    path('user-details/', views.UserDetails.as_view(),name="userdetailsapi"),
    path('edit-profile/', views.EditProfile.as_view(),name="editprofileapi"),
    path('edit-mobile/', views.EditMobile.as_view(),name="editmobileapi"),
    path('edit-email/', views.EditEmail.as_view(),name="editemailapi"),
    path('change-password/', views.ChangePassword.as_view(),name="changepasswordapi"),
    
    path('address/', views.AddressAPI.as_view(),name="addressapi"),
    path('cartaddress/', views.CartAddressAPI.as_view(),name="cartaddressapi"),
    
    
    path('create-user/', views.CreateUser.as_view(),name="createuser"),
    path('login/', views.UserLogin.as_view(),name="userlogin"),
    path('forgotpassword/', views.UserForgotPassword.as_view(), name="userforgotpassword"),


]
