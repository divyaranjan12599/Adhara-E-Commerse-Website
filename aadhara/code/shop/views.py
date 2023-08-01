from os import name
from django.shortcuts import render
from django.views.generic import TemplateView, View
from core.utils import build_breadcrumb, build_html_head, sort_products, sort_options
from core import choices
from django.urls import reverse
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from .models import Product,Cart,Order,Category,ProductOption,DiscountCoupon, ProductOptionAttributes,Attribute
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from core.models import Configuration
from users.models import Address
from django.core import signing

from django.core.mail import send_mail
from django.conf import settings as conf_settings
from shop.mails import order_placed_communication
from datetime import datetime, date
# Create your views here.

class ProductDetailView(TemplateView):
    template_name = "storefront/shop/product/detail.html"


    def get_context(self, request,product_id,slug, *args, **kwargs):
        product = get_object_or_404(Product,pk=product_id,slug=slug)
        ctx= product.get_detail_page_context(request)
        ctx['lightbox_enabled']=True
        return ctx
        
    def get(self, request,product_id,slug, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request,product_id,slug, args, kwargs))


class ProductListView(TemplateView):
    template_name = "storefront/shop/product/list.html"

    def get_context(self,request,id,slug, *args, **kwargs):
        category = get_object_or_404(Category,id=id,slug=slug)
        return category.get_option_list_context(request)

    def get(self, request,id, slug, *args, **kwargs):
        template=self.template_name
        if request.GET.get('ajax'):
            # print("In ajax call")
            template = "storefront/shop/product/includes/sidebar.html"
        if request.GET.get('pagination_ajax'):
            template = "storefront/shop/product/includes/list-ajax.html"
        return render(request, template, self.get_context(request,id, slug, args, kwargs))


class CartView(TemplateView):
    template_name = "storefront/shop/cart.html"

    def get_context(self, request, *args, **kwargs):
        return Cart.common_context()

    def get(self, request, *args, **kwargs):
        cart = Cart.get_cart(request,False)
        if request.GET.get('remove_coupon'):
            cart.discount_coupon = None
            cart.save()
            cart.update_cart_discount_amount()
            return redirect(reverse('shop:cart'))
        return render(request, self.template_name, self.get_context(request, args, kwargs))

    def post(self,request,*args, **kwargs):
        current_date = date.today()
        coupon_code =request.POST.get('code',False)
        coupon_obj = DiscountCoupon.objects.filter(code__iexact=coupon_code,start_date__lte=current_date,end_date__gte=current_date).last()
        cart = Cart.get_cart(request,False)
        ctx=self.get_context(request,args,kwargs)
        if coupon_obj and cart.total_without_tax >= coupon_obj.min_cart_amount:
            cart.discount_coupon = coupon_obj
            # print(cart.discount_coupon)
            cart.save()
            cart.update_cart_discount_amount()
        elif coupon_code:
            ctx["Invalid_coupon"]=True
        return render(request, self.template_name, ctx)

class CheckoutView(TemplateView):
    template_name = "storefront/shop/checkout.html"
    
    def get_context(self, request, *args, **kwargs):
        ctx= Cart.common_context()
        # ctx['addresses'] = request.user.addresses()
        cart = Cart.get_cart(request)
        can_checkout, message = cart.can_checkout() if cart else (False, "Please add few products before proceeding")
        ctx['can_checkout'] = can_checkout
        ctx['can_checkout_message'] = message
        ctx['address'] = Address.get(request)
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, args, kwargs))


class OrderPlacedView(TemplateView):
    template_name = "storefront/shop/order-placed.html"
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get_context(self, request, *args, **kwargs):
        ctx= Order.common_context()
        order = request.session.get('RECENT_ORDER')
        if not order:
            raise Exception("No order")
        ctx['order'] = Order.objects.get(pk=order)
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request, args, kwargs))


class OrderRetryPaymentView(TemplateView):
    template_name = "storefront/shop/order-retry-payment.html"
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get_context(self, request,order_id, *args, **kwargs):
        ctx= Order.common_context()
        order = Order.objects.filter(pk=signing.loads(order_id)).first()
        if not order:
            raise Exception("No order")
        ctx['order'] = order
        
        return ctx

    def get(self, request,order_id, *args, **kwargs):
        return render(request, self.template_name, self.get_context(request,order_id, args, kwargs))

from django.urls import resolve
class SearchView(TemplateView):
    template_name = "storefront/shop/product/list.html"

    def get_context(self,request,query, *args, **kwargs):
        ctx = {}
        title,description = "{} Search".format(query),''
        ctx['html_head'] = build_html_head(title=title,description=description)
        products = Product.search(query)
        category = Category()
        ctx['category'] = category
        options = ProductOption.objects.filter(product__in=products).distinct()
        ctx['filters'] = category._options_filters_sidebar(options)
        options,ctx['selected_filters']=category._filter_options(options,request)
        options=category.duplicate_remover(options)
        options = sort_options(options,request.GET.get('sortby',False)) 
        paginator = Paginator(options, Configuration.get('product_listsize',25))  # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        ctx['title']="{} Search Results".format(query)
        ctx['query'] = query
        ctx['page_obj'] = page_obj
        return ctx


    def get(self, request,*args, **kwargs):
        query = request.GET.get('q',False)
        if not query:
            return redirect("/")
        return render(request, self.template_name, self.get_context(request,query, args, kwargs))
