from django.db.models.query_utils import Q
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, View
from core.utils import build_breadcrumb, build_html_head
from core.models import CityState,Pincode,Configuration,TextPlaceholder
from django.urls import reverse
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from .models import  User, Address
from django.core.paginator import Paginator
from shop.models import Order,Cart,OrderProducts,OrderPayment
import math
from django.contrib.auth.decorators import user_passes_test
from core import choices
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings as conf_settings
from shop.mails import registration_success_communication, password_change_communication
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm,\
    PasswordResetForm,SetPasswordForm      
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash,get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.messages.views import SuccessMessageMixin


# Create your views here.

class RegisterView(TemplateView):
    template_name = "storefront/users/register.html"

    def breadcrumb(self):
        l = [{
            'title': "Register",
            'text': "Register",
            'url': reverse('users:register')
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s = "Register with {}".format(Configuration.get('SITE_NAME'))
        return build_html_head(title=s, description=s)

    def get_context(self, request, *args, **kwargs):
        ctx = {}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        ctx['maximum_date'] = datetime.now() - relativedelta(years=18)
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, args, kwargs))


    def post(self, request, *args, **kwargs):
        ctx = self.get_context(request, args, kwargs)
        name=request.POST.get('name',False)
        mobile=request.POST.get('mobile',False)
        email=request.POST.get('email',False)
        password=request.POST.get('password',False)
        password2=request.POST.get('password2',False)
        status,message=False,""
        if User.objects.filter(Q(mobile=mobile)|Q(email=email)):
            status,message=False,"User with this email or mobile already existing, try <a href='{}'>resetting password</a>.".format(reverse('users:resetpassword'))
        else:
            if password == password2:
                user =User()
                user.name=name
                user.email=email
                user.mobile=mobile
                user.set_password(password)
                user.save()
                registration_success_communication(user)
                return redirect(reverse('users:login'))
            else:
                status,message=False,"Entered passwords do not match, please enter again."
                
        ctx['status']=status
        ctx['message']=message
        return render(request, self.template_name, ctx)

class LoginView(TemplateView):
    template_name = "storefront/users/login.html"

    def breadcrumb(self):
        l = [{
            'title': "Login",
            'text': "Login",
            # 'url':reverse('login')
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s = "Login"
        return build_html_head(title=s, description=s)

    def get_context(self, request, *args, **kwargs):
        ctx = {}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        return ctx

    def get(self, request, *args, **kwargs):
        from_checkout=request.GET.get('from_checkout',False)
        if from_checkout:
            request.session['from_checkout'] = True
            
        return render(request, self.template_name, self.get_context(request, args, kwargs))
    
    def post(self,request,*args,**kwargs):
        data=self.get_context(request,args,kwargs)
        data['status']= False
        data['message'] = "All Fields Required"
        email_or_phone = request.POST.get('email_or_phone',False)
        password = request.POST.get('password',False)
        next_page_url = request.POST.get('next_page_url',False)
        if email_or_phone and password:
            user = authenticate(username=email_or_phone,password=password)
            if user:
                data['status']=True
                data['message'] = "Logged In"
                login(request,user)
                if request.session.get('from_checkout',False):
                    del request.session['from_checkout']
                    return redirect(reverse('shop:checkout'))
                elif next_page_url:
                    return redirect(next_page_url)
                else:
                    return redirect(reverse('core:homepage'))
            else:
                data['message']="Login failed. Invalid username/password."
        return render(request, self.template_name,data)


class  PasswordResetConfirmView(SuccessMessageMixin,auth_views.PasswordResetConfirmView):
    template_name = 'storefront/users/passwords/password_reset_confirm.html' 
    title = 'Password reset sent'
    success_url = reverse_lazy('users:login')
    form_class=SetPasswordForm
    success_message='Password changed successfully.'



    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        title='Set Password'
        ctx['meta_title']=title
        ctx['html_head']={'title':title,'description':''}
        # ctx['message']="Email Sent successfully."
        return ctx
    


class PasswordResetFormAllowNoActive(PasswordResetForm):
    
    def get_users(self, email):
        all_users = get_user_model()._default_manager.filter(
            email__iexact=email)
        return all_users


class ForgotPasswordView(SuccessMessageMixin,auth_views.PasswordResetView,TemplateView):
    template_name = "storefront/users/passwords/forgot_password.html" 
    form_class = PasswordResetForm
    email_template_name='mail/user/password_reset_email.html'
    success_message='Email Sent Successfully'

    def breadcrumb(self):
        l = [{
            'title': "Forgot Password",
            'text': "Forgot Password",
            # 'url':reverse('login')
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s = "Forgot Password"
        return build_html_head(title=s, description=s)

    def get_context(self, request, *args, **kwargs):
        ctx = {}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, args, kwargs))


def logout(request):
    auth_logout(request)
    return redirect("/")


class MyAccountView(TemplateView):
    template_name = "storefront/users/account.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def breadcrumb(self):
        l = [{
            'title': "My Account",
            'text': "My Account",
            'url': reverse('users:account')
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s = "My Account"
        return build_html_head(title=s, description=s)

    def get_context(self, request, *args, **kwargs):
        ctx = {}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        ctx['email'] = request.user.email
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, args, kwargs))


class Error404View(TemplateView):
    template_name = "404.html"

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def breadcrumb(self):
        l = [{
            'title': "Page Not Found",
            'text': "Page Not Found",
            'url': '/'
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s = "Error 404"
        return build_html_head(title=s, description=s)

    def get_context(self, request, *args, **kwargs):
        ctx = {}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, args, kwargs))



class WishlistView(TemplateView):
    template_name = "storefront/users/wishlist.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def breadcrumb(self):
        l = [{
            'title': "My Account",
            'text': "My Account",
            'url': reverse('users:account')
        },{
            'title': "Wishlist",
            'text': "Wishlist",
            'url': reverse('users:account')
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s = "My Wishlist"
        return build_html_head(title=s, description=s)

    def get_context(self, request, *args, **kwargs):
        ctx = {}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        ctx['wishlist_items'] = request.user.wishlist()
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, args, kwargs))



class AddEditAddressView(TemplateView):
    template_name = "users/add-address.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def breadcrumb(self):
        l = [{
            'title': "My Account",
            'text': "My Account",
            'url': reverse('users:account')
        }, {
            'title': "Addresses",
            'text': "Address",
            'url': reverse('users:account')
        }, {
            'title': "Add/Edit",
            'text': "Add/Edit",
            'url': ''
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s = "Add/Edit Address:: My Account"
        return build_html_head(title=s, description=s)

    def get_context(self, request, *args, **kwargs):
        ctx = {}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        ctx['bankdetails'] = BankDetails.objects.filter(user=request.user).first()
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, args, kwargs))


def logout(request):
    auth_logout(request)
    return redirect("/")


class EditProfileView(TemplateView):
    template_name = 'storefront/users/edit-profile.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def breadcrumb(self):

        l = [{
            'title': "My Account",
            'text': "My Account",
            'url': reverse('users:account')
        }, {
            'title': 'Edit Profile',
            'text': 'Edit Profile',
            'url': ''
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s='Edit My Profile'
        return build_html_head(title=s, description=s)

    def get_context(self, request, *args, **kwargs):
        ctx={}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, *args, **kwargs))

    def post(self, request, *args, **kwargs):
        ctx = self.get_context(request, args, kwargs)
        name=request.POST.get('name',False)
        mobile=request.POST.get('mobile',False)
        email=request.POST.get('email',False)
        user = request.user
        if User.objects.filter(Q(email=email)|Q(mobile=mobile),~Q(id=user.id)).exists():
            messages.error(request, "User with this email or mobile already existing, try <a href='{}'>resetting password</a>.".format(reverse('users:resetpassword')) )
            return redirect(reverse('users:editprofile'))
        else:
            user.name=name
            user.email=email
            user.mobile=mobile
            user.save()
            messages.success(request, 'Profile details updated.')
        return redirect(reverse('users:account'))


class ChangePasswordView(TemplateView):
    template_name = 'storefront/users/passwords/change-password.html'


    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def breadcrumb(self):

        l = [{
            'title': "My Account",
            'text': "My Account",
            'url': reverse('users:account')
        }, {
            'title': 'Edit Profile',
            'text': 'Edit Profile',
            'url': ''
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s='Edit My Profile'
        return build_html_head(title=s, description=s)

    def get_context(self, request, *args, **kwargs):
        ctx={}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, *args, **kwargs))

    def post(self, request, *args, **kwargs):
        ctx = self.get_context(request, args, kwargs)
        password=request.POST.get('password',False)
        password2=request.POST.get('password2',False)
        status,message=False,""
        user = request.user
        if user.check_password(password):
            status,message=False,"Entered passwords cannot match the previous password"
        elif password == password2:
            user.set_password(password)
            update_session_auth_hash(request, user)
            user.save()
            messages.success(request, 'Password changed successfully.')
            password_change_communication(user)
            return redirect(reverse('users:account'))
        else:
            status,message=False,"Entered passwords do not match, please try again."

        ctx['status']=status
        ctx['message']=message
        return render(request, self.template_name, ctx)



class MyAddressesView(TemplateView):
    template_name = 'storefront/users/my-addresses.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def breadcrumb(self):

        l = [{
            'title': "My Account",
            'text': "My Account",
            'url': reverse('users:account')
        }, {
            'title': 'Billing/Shipping Address',
            'text': 'Billing/Shipping Address',
            'url': ''
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s='Billing/Shipping Address'
        return build_html_head(title=s, description=s)

    def get_context(self, request, *args, **kwargs):
        ctx={}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        ctx['address'] = Address.objects.filter(user=request.user).first()
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, *args, **kwargs))


class AddressAddEditView(TemplateView):
    template_name = 'storefront/users/address-add-edit.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def breadcrumb(self):

        l = [{
            'title': "My Account",
            'text': "My Account",
            'url': reverse('users:account')
        }, {
            'title': 'Billing/Shipping Address',
            'text': 'Billing/Shipping Address',
            'url': reverse('users:myaddresses')
        }, {
            'title': 'Add/Edit',
            'text': 'Add/Edit',
            'url': reverse('users:myaddresses')
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s='Add/Edit Address'
        return build_html_head(title=s, description=s)

    def get_context(self,request, *args, **kwargs):
        ctx={}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        address_id =request.GET.get('address_id',0)
        address = Address.objects.filter(pk=address_id,user=request.user).first()
        ctx['address'] = address or Address()
        ctx['address_status'] = (address_id and address) or address_id == 0
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, *args, **kwargs))


    def post(self,request, *args, **kwargs):
        try:
            a=Address()
            address_id = request.POST.get('address_id',False)
            if address_id:
                existing_address = Address.objects.filter(user=request.user,id=address_id).first()
                if existing_address:
                    a = existing_address
                
            a.name = request.POST.get('name',False)
            a.address = request.POST.get('address',False)
            a.mobile = request.POST.get('mobile',False)
            a.email = request.POST.get('email',False)
            state = request.POST.get('state',False)
            statename = CityState.objects.filter(name=state).first()
            if statename:
                s = statename
            else:
                s = CityState()
                s.name = state
                s.type = 2
                s.save()
            a.state = s
            city = request.POST.get('city',False)
            cityname = CityState.objects.filter(name=city).first()
            if cityname:
                c = cityname
            else:
                c = CityState()
                c.name = city
                c.parent = s
                c.type = 4
                c.save()
            a.city = c
            pincode = request.POST.get('pincode',False)
            pin = Pincode.objects.filter(pincode=pincode).first()
            if pin:
                p = pin
            else:
                p = Pincode()
                p.pincode = pincode
                p.city_state = c
                p.save()
            a.pincode = p
            a.user = request.user
            a.save()
            if address_id:
                messages.success(request, 'Address changed successfully.')
            else:
                messages.success(request, 'Address added successfully.')

        except Exception as e:
            # print("excpeitasdfas",e)
            ctx=self.get_context(request, *args, **kwargs)
            ctx['status'] = False
            ctx['message'] = "Something went wrong "+str(e) 
            return render(request, self.template_name, ctx)
        
        return redirect(reverse('users:myaddresses') + "?addresscreated=yes")





class MyOrdersView(TemplateView):
    template_name = 'storefront/users/my-orders.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def breadcrumb(self):

        l = [{
            'title': "My Account",
            'text': "My Account",
            'url': reverse('users:account')
        }, {
            'title': 'My Orders',
            'text': 'My Orders',
            'url': reverse('users:myaddresses')
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s='My Orders'
        return build_html_head(title=s, description=s)

    def get_context(self,request, *args, **kwargs):
        ctx={}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        orders = Order.objects.filter(user=request.user).exclude(order_status=choices.OrderStatus.CANCELED).order_by('-id')
        ctx['orders'] = orders
        products = []
        for order in orders:
            products.append(OrderProducts.objects.filter(order=order))
        ctx['products'] = products
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, *args, **kwargs))


class OrderDetailsView(TemplateView):
    template_name = 'storefront/users/order-details.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def breadcrumb(self):

        l = [{
            'title': "My Account",
            'text': "My Account",
            'url': reverse('users:account')
        }, {
            'title': 'My Orders',
            'text': 'My Orders',
            'url': reverse('users:orders')
        }, {
            'title': 'Order Details',
            'text': 'Order Details',
            'url': ''
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s='Order Details'
        return build_html_head(title=s, description=s)

    def get_context(self,request, *args, **kwargs):
        ctx={}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        order_id = request.GET.get('order_id',0)
        ctx['order'] = get_object_or_404(Order,id=order_id,user=request.user) 
        ctx['products'] = OrderProducts.objects.filter(order=order_id)
        ctx['gateway'] = OrderPayment.objects.filter(order=order_id).first()
        ctx['order_status']=[choices.OrderStatus.SHIPPED,choices.OrderStatus.COMPLETE]
    
        if ctx['order'].order_status in ctx['order_status']:
            ctx['shipping_awb_no']=ctx['order'].shipping_awb_no()
            ctx['shipping_courier_name']=ctx['order'].shipping_courier_name()
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, *args, **kwargs))



      

class InvoiceView(TemplateView):
    template_name = 'storefront/users/invoice.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    
    
    def get_context(self,request, *args, **kwargs):
        ctx={}
        order_id = request.GET.get('order_id',0)
        if request.user.is_superuser:
            ctx['order'] =get_object_or_404(Order,id=order_id)
        else:
            ctx['order'] = get_object_or_404(Order,id=order_id,user=request.user)
        ctx['date_format']='%d-%b-%Y'
        ctx['customer_care_no'] = Configuration.get('customer_care_no','9999999999')  
        ctx['date_format'] = Configuration.get('date_format',"%d %b %Y")
        ctx['INVOICE_FOOTER_TEXT'] = TextPlaceholder.get('INVOICE_FOOTER_TEXT','I hereby confirm that said above goods are being purchased for my internal or personal purpose and not for re-sale. I further understand and agree to Aadhara Terms & conditions/Terms of Use/Privacy Policy/Return Policy/FAQ/News & change of policies on website is reserved by company. We declare that this invoice shows the actual price of the goods described & that all particulars are true and correct. Subjected to Jaipur, Rajasthan Juridiction.')
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, *args, **kwargs))

