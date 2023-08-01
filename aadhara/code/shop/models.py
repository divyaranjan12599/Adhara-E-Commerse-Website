from django.db import models
from core.models import BaseTechvinsModel,CityState
from core import choices
from core.models import Pincode,CityState,Configuration
from django.utils.text import slugify
from core.utils import build_breadcrumb, build_html_head,price_format
from django.urls import reverse
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from ecommerce.jinja_env import img_tag
from shop.payment.razorpay import RazorpayService
from simple_history.models import HistoricalRecords
from django.db.models import F, Sum, FloatField, Avg, Max
import math
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from datetime import datetime
from ecommerce.jinja_env import img_tag
from django.utils.html import mark_safe
from core.utils import per_cent_amount,per_cent_tax
from users.models import Address,User
from django.db.models import Q
from ckeditor.fields import RichTextField
from core.utils import sort_products,sort_options
from django.core import signing
from django.utils import timezone
# Create your models here.


def get_invoice_number(now=False):
    if not now:
        now = datetime.now()
    #GET FROM DB
    key = 'invoice_inc_number'
    date = now.strftime('%y%m')
    value = "{},{}".format(date,1)
    invoice_incr_number = Configuration.get(key,default=value,editable=False)
    numbers = invoice_incr_number.split(',')
    number = int(numbers[1])
    if int(date) >int(numbers[0]):
        number = 1 
    
    invoice_number = "INV{}{}".format(date,number)
    
    
    c=Configuration.objects.get(key=key,editable=False)
    
    value = "{},{}".format(date,number+1)
    c.value = value
    c.save()
    return invoice_number

class SlugModel(models.Model):
    slug=models.SlugField(max_length=255)
    history = HistoricalRecords()

    def get_slug_field(self):
        return 'name'

    def save(self, *args, **kwargs):
        self.slug = slugify(getattr(self,self.get_slug_field()))
        super(SlugModel, self).save(*args, **kwargs)
        
    class Meta:
        abstract = True

    def __str__(self):
        return "{}".format(getattr(self,self.get_slug_field()))

class DiscountCategory(BaseTechvinsModel,SlugModel):
    name=models.CharField(max_length=200,blank=True,null=True)
    category_type = models.PositiveSmallIntegerField(choices=choices.DiscountCategoryType.CHOICES,default=choices.DiscountCategoryType.ALL)
    min_cart_amount = models.FloatField(default=0)
    type = models.PositiveSmallIntegerField(choices=choices.DiscountType.CHOICES,default=choices.DiscountType.PERCENTAGE)
    value = models.FloatField("Percentage or Fix amount of discount",blank=True,null=True)
    start_date_time= models.DateTimeField()
    end_date_time = models.DateTimeField()

    def get_label(self):
        return "Special Discount({}{})".format(self.value,'%' if self.type == choices.DiscountType.PERCENTAGE else '₹')

    def get_discount(self,amount):
        return int(round((amount*self.value)/100)) if self.type == choices.DiscountType.PERCENTAGE else self.value


    class Meta:
        verbose_name_plural = "Discount Categories"


    @classmethod
    def get_for_cart(cls,cart):
        cart_amount = cart.total_price_without_tax(formatted=False)
        now=datetime.now()
        dc= DiscountCategory.objects.filter(category_type=choices.DiscountCategoryType.ALL,
                        min_cart_amount__lte=cart_amount,start_date_time__lte=now,end_date_time__gte=now).order_by('-min_cart_amount').first()
        return dc

    @property
    def edit_url(self):
        return reverse('shopadmin:editdiscountcategory',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deletediscountcategory',args=[self.id])
    
class DiscountCoupon(BaseTechvinsModel):
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    discount_value = models.FloatField(default=0)
    discount_type = models.PositiveSmallIntegerField(choices=choices.DiscountType.CHOICES)
    max_discount = models.FloatField(default=0)
    min_cart_amount = models.FloatField(default=0)
    summary=models.CharField(max_length=300,null=True,blank=True)
    discount_image=models.ImageField(upload_to="discount_image",null=True,blank=True)
    coupon_type=models.PositiveSmallIntegerField(choices=choices.DiscountCouponType.CHOICES,
        default=choices.DiscountCouponType.ALL_PURCHASES,
        help_text="Apply discount on all purchases or on first purchase")
    
    @classmethod
    def get_eligible_coupons(cls,cart):
        now =timezone.now()
        coupons = DiscountCoupon.objects.filter(start_date__lte=now,end_date__gte=now)
        if cart.is_first_time_order():
            return coupons
        return coupons.exclude(coupon_type=choices.DiscountCouponType.FIRST_PURCHASE)

    def get_discount(self,amount):
        return int(round((amount*self.discount_value)/100)) if self.discount_type == choices.DiscountType.PERCENTAGE else self.discount_value
        
    def discount_type_is_percentage(self):
        if self.discount_type == choices.DiscountType.PERCENTAGE:
            return True
        return False
    
    @property
    def edit_url(self):
        return reverse('shopadmin:editdiscountcoupon',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deletediscountcoupon',args=[self.id])
    
class Manufacturer(BaseTechvinsModel,SlugModel):
    name=models.CharField(max_length=255)
    
    @property
    def edit_url(self):
        return reverse('shopadmin:editmanufacturer',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deletemanufacturer',args=[self.id])
    
class Category(BaseTechvinsModel,SlugModel):
    name=models.CharField(max_length=255)
    parent = models.ForeignKey('self',blank=True,null=True,on_delete=models.SET_NULL,related_name="children")
    priority = models.PositiveSmallIntegerField(default=1,help_text="1 is higher than 2")
    size_chart = RichTextField(blank=True)
    shipping_and_returns = RichTextField(blank=True)
    placeholder = models.TextField(max_length=528,blank=True,null=True)
    def __str__(self):
        parent_name = ""
        if self.parent:

            parent_name = self.parent
        return "{} | {}".format(parent_name,self.name)
    class Meta:
        verbose_name_plural = "Categories"

    @property
    def edit_url(self):
        return reverse('shopadmin:editcategory',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deletecategory',args=[self.id])

    def get_title_description(self):
        txt =  "Buy {} Online in India".format(self.name)
        return txt,txt

    def _my_breadcrumb(self):

        home = {}
        home['title'] = "{}".format(self.name)
        home['url'] = reverse('shop:productlist',args=[self.slug,self.id])
        home['text'] = "{}".format(self.name)
        return home

    def breadcrumb(self):
        # return build_breadcrumb([])

        lst = []
        lst.append(self._my_breadcrumb())
        parent = self.parent
        while parent:
            lst.append(parent._my_breadcrumb())
            parent = parent.parent
        lst.reverse()
        return build_breadcrumb(lst)

    def get_child_categories(self):
        return Category.objects.filter(parent=self).order_by('priority')

    
    def _filters(self,products):
        d={}
        if products:
            price_sorted_products=products.order_by('options__selling_price')
            d['min_price']=price_sorted_products.first().options.first().selling_price
            d['max_price']=price_sorted_products.last().options.last().selling_price
            d['sizes']=ProductOptionAttributes.objects.filter(attribute__name="Size",
                    product_option__product__in=products).values('value').distinct()
            d['colors']=ProductOptionAttributes.objects.filter(attribute__name="Color",
                    product_option__product__in=products).values('value').distinct()
            d['fabrics']=ProductAttributes.objects.filter(name = 'Fabric').values('value').distinct()
            d['brands']=Manufacturer.objects.filter(pk__in=products.values_list('manufacturer_id')).distinct()
        return d
    
    def _options_filters_sidebar(self,options):
        #print("In options_filters_sidebar")
        d={}
        if options:
            products=options.values_list('product')
            min_price,max_price=999999999,0
            for option in options:
                min_price=min(min_price,option.selling_price)
                max_price=max(max_price,option.selling_price)
            d['min_price']=min_price
            d['max_price']=max_price
            d['sizes']=ProductOptionAttributes.objects.filter(attribute__name="Size",
                    product_option__product__in=products).values('value').distinct().order_by('priority')
            d['colors']=ProductOptionAttributes.objects.filter(attribute__name="Color",
                    product_option__product__in=products).values('value').distinct()
            d['fabrics']=ProductAttributes.objects.filter(name = 'Fabric').values('value').distinct()
            
            # d['brands']=Manufacturer.objects.filter(pk__in=products.values_list('manufacturer_id')).distinct()
        return d
    
    def _parse_request_filters(self,request):
        #print("In parse_request_filters")
        selected_filters={}
        size_filter=request.GET.get('size','').split('--')
        if size_filter:
            selected_filters['size']=[item for item in size_filter if item != '']
        
        color_filter=request.GET.get('color','').split('--')
        if color_filter:
            selected_filters['color']=[item for item in color_filter if item != '']
            
        fabric_filter=request.GET.get('fabric','').split('--')
        if fabric_filter:
            selected_filters['fabric']=[item for item in fabric_filter if item != '']
        
        amount_filter=request.GET.get('amount','').split('-')
        amount_filter=[item for item in amount_filter if item != '']
        if amount_filter:
            selected_filters['min_price']=int(amount_filter[0].replace('₹', ''))
            
            selected_filters['max_price']=int(amount_filter[1].replace('₹', ''))



        return selected_filters

    def _filter_products(self,products,request):
      
        selected_filters = self._parse_request_filters(request)
        if selected_filters.get('size'):
            products=products.filter(options__attributes__attribute__name="Size",options__attributes__value__in=selected_filters.get('size')).distinct()
        if selected_filters.get('color'):
            products=products.filter(options__attributes__attribute__name="Color",options__attributes__value__in=selected_filters.get('color')).distinct()
      
        return products,selected_filters

    
    def _filter_options(self,options,request):
        #print("In filter_options")
        selected_filters = self._parse_request_filters(request)
        # print("selected_filters.get('size')",selected_filters)
        if selected_filters.get('size'):
            options=options.filter(attributes__attribute__name="Size",attributes__value__in=selected_filters.get('size')).distinct()
        if selected_filters.get('color'):
            options=options.filter(attributes__attribute__name="Color",attributes__value__in=selected_filters.get('color')).distinct()
        if selected_filters.get('fabric'):
            products=ProductAttributes.objects.filter(value__in=selected_filters.get('fabric')).values('product').distinct() 
            options = options.filter(product__in = products)
            
        if selected_filters.get('min_price') and selected_filters.get('max_price'):
            ids=[]
            for option in options:
                option_price=option.selling_price
                if selected_filters.get('min_price') <= option_price <=selected_filters.get('max_price'):
                    ids.append(option.id)
            options = options.filter(id__in=ids)

        return options,selected_filters
        
    def get_product_list_context(self,request):
        ctx = {}
        title,description = self.get_title_description()
        ctx['html_head'] = build_html_head(title=title,description=description)
        ctx['breadcrumb'] = self.breadcrumb()
        products = self._get_products()
        
        ctx['filters'] = self._filters(products)
        products,ctx['selected_filters']=self._filter_products(products,request)
        print(products,ctx['selected_filters'])
        products = sort_products(products,request.GET.get('sortby',False))        
        # products = Product.objects.all()
        paginator = Paginator(products, Configuration.get('product_list_size',25))  # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # print(dir(page_obj.paginator))
        ctx['page_obj'] = page_obj
        ctx['category'] = self
        ctx['title']=self.name
        return ctx


    def get_option_list_context(self,request):
        ctx = {}
        title,description = self.get_title_description()
        ctx['html_head'] = build_html_head(title=title,description=description)
        ctx['breadcrumb'] = self.breadcrumb()
        options = self._get_options()
        
        ctx['filters'] = self._options_filters_sidebar(options)
        options,ctx['selected_filters']=self._filter_options(options,request)
        options=self.duplicate_remover(options)
        options = sort_options(options,request.GET.get('sortby',False))        
        # options = Product.objects.all()
        paginator = Paginator(options, Configuration.get('product_list_size',25))  # Show 25 contacts per page.
        page_number = request.GET.get('page',1)
        page_obj = paginator.get_page(page_number)
        # print(dir(page_obj.paginator))
        ctx['page_obj'] = page_obj
        ctx['category'] = self
        ctx['title']="Shop for {}".format(self.name)
        
        return ctx


    def all_children(self):
        all = [self]
        children = Category.objects.filter(parent__in=all)
        while children:
            all.extend(children)
            children = Category.objects.filter(parent__in=children)
        return all

    @property
    def child_categories(self):
        return Category.objects.filter(parent=self)

    def _get_products(self):
        return Product.objects.filter(status=choices.StatusChoices.ENABLED)\
            .filter(Q(primary_category__in=self.all_children()) | Q(categories__in=self.all_children() )).distinct()

    def _get_options(self):
        #print("In get_options")
        options=ProductOption.objects.filter(product__status=choices.StatusChoices.ENABLED)\
            .filter(Q(product__primary_category__in=self.all_children()) | Q(product__categories__in=self.all_children() )).distinct()
        return options

    def duplicate_remover(self,options):
        #print("In duplicate_remover")
        duplicate_remover={}
        lst=[]
        for o in options:
            if o.product not in duplicate_remover:
                duplicate_remover[o.product]=[]
            identifier=o.attributes.filter(attribute=o.product.primary_attribute).first().value
            if identifier not in duplicate_remover[o.product]:
                lst.append(o.id)
                duplicate_remover[o.product].append(identifier)

        return options.filter(id__in=lst)
                    

    def url(self):
        return reverse('shop:productlist',args=[self.slug,self.id])


    def featured_products(self,limit=10):
        return self._get_products().order_by('-modified')[:limit]

    def new_products(self,limit=10):
        return self.featured_products(limit)

class HomepageCategory(BaseTechvinsModel):
    category=models.ForeignKey('shop.Category',null=True,on_delete=models.SET_NULL)
    enabled = models.BooleanField(default=False)
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=120,blank=True)
    button_text = models.CharField(max_length=120)
    priority = models.PositiveSmallIntegerField(default=1,help_text="1 is higher than 2")
    image = models.ImageField(upload_to="upload/homepage/",null=True,max_length=250,help_text="minimum width: 775px")
    
    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name_plural = "Homepage Categories"

    @property
    def edit_url(self):
        return reverse('shopadmin:edithomepagecategory',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deletehomepagecategory',args=[self.id])

class TaxClass(BaseTechvinsModel):
    name = models.CharField(max_length=200,null=True,blank=True)
    description = models.TextField(max_length=200,blank=True,null=True)

    class Meta:
        verbose_name_plural = "Tax Classes"

    @property
    def edit_url(self):
        return reverse('shopadmin:edittaxclass',args=[self.id])

    @property
    def delete_url(self):
        return reverse("shopadmin:deletetaxclass",args=[self.id])

    def __str__(self):
        return "{}".format(self.name)

    def bracket(self,rate):
        bracket = self.brackets.all().filter(min_rate__lte=rate,max_rate__gte=rate).last()
        if bracket:
            return bracket
        return TaxClassBracket.objects.first()

class TaxClassBracket(models.Model):
    tax_class= models.ForeignKey(TaxClass,on_delete=models.CASCADE,related_name="brackets")
    min_rate = models.FloatField(default=0)
    max_rate=models.FloatField(default=0)
    cgst_rate = models.FloatField(default=0)
    sgst_rate = models.FloatField(default=0)
    igst_rate = models.FloatField(default=0)

    @property
    def total_rate(self):
        return self.igst_rate

    def total_amount(self,rate):
        return self._calculate_rate(rate,self.igst_rate)

    def cgst_amount(self,rate):
        return self._calculate_rate(rate,self.cgst_rate)

    def igst_amount(self,rate):
        return self._calculate_rate(rate,self.igst_rate)

    def sgst_amount(self,rate):
        return self._calculate_rate(rate,self.sgst_rate)

    def _calculate_rate(self,rate,percentage):
        return per_cent_tax(rate,percentage,use_ceil=True)
        # return per_cent_amount(rate,percentage,use_ceil=True)

    def __str__(self):
        return "{}: {}-{}".format(self.tax_class.name,self.min_rate,self.max_rate)



class Attribute(BaseTechvinsModel,SlugModel):
    name=models.CharField(max_length=255)
    
    @property
    def edit_url(self):
        return reverse('shopadmin:editattribute',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deleteattribute',args=[self.id])

class Product(BaseTechvinsModel,SlugModel):
    name=models.CharField(max_length=255)
    summary=models.CharField(max_length=512,blank=True,null=True)
    manufacturer = models.ForeignKey('Manufacturer',null=True, on_delete=models.SET_NULL)
    primary_category = models.ForeignKey('Category',null=True,on_delete=models.SET_NULL,related_name="products")
    categories = models.ManyToManyField('Category')
    description=models.TextField(blank=True,null=True)
    hsn = models.CharField(max_length=100,blank=True,null=True)
    sku = models.CharField(max_length=100,blank=True,null=True)
    location = models.ForeignKey(CityState,null=True,blank=True,on_delete=models.SET_NULL)
    status = models.SmallIntegerField(choices=choices.StatusChoices.CHOICES, default=choices.StatusChoices.DISABLED)
    return_days = models.SmallIntegerField( default=0)
    youtube_link=models.URLField(max_length=200,blank=True,null=True)
    weight_gram = models.PositiveSmallIntegerField(default=0)
    tax_class = models.ForeignKey(TaxClass,null=True, on_delete=models.SET_NULL)

    primary_attribute = models.ForeignKey(Attribute,on_delete=models.SET_NULL,null=True,help_text="eg. color is the primary attribute for kurti")
    width=models.CharField(max_length=120,blank=True,null=True)
    height=models.CharField(max_length=120,blank=True,null=True)
    length=models.CharField(max_length=120,null=True,blank=True)
    def get_title_description(self):
        return self.name, self.summary

    @classmethod
    def search(cls,query):
        return Product.objects.filter(name__icontains=query)

    @property
    def category(self):
        return self.primary_category
        
    def breadcrumb(self):
        breadcrumb = self.primary_category.breadcrumb()
        l = {
            'title': self.name,
            'text': self.name,
            'url': ''
            }
        
        breadcrumb.append(l)
        return breadcrumb

    def is_on_sale(self):
        #TODO
        return True

    def image_tag(self):
        try:
            from django.utils.html import escape
            option = self.get_option(None)
            return mark_safe('<a href="{}" target=_BLANK><img src="{}" width="50" height="50" /></a>'.format(self.url(), img_tag(size="100/100",src=option.image().image.url,url_only=True) ))
        except Exception as e:
            # print("ecasd",e)
            return mark_safe('<img width=50 height=50>')

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def get_detail_page_context(self,request):
        ctx = {}
        title,description = self.get_title_description()
        ctx['html_head'] = build_html_head(title=title,description=description)
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['product'] = self
        option=self.get_option(request)
        ctx['option'] = option
        ctx['option_attributes'] = self.get_option_attributes(option)
        ctx['related_products'] = Product.objects.exclude(id=self.id).order_by('-modified')[:5]
        r=self.recent_viewed(request)
        ctx['recently_viewed_products']=r
        return ctx

    def recent_viewed(self,request):
        recently_viewed_products={}
        if 'recently_viewed' in request.session:
            if self.pk in request.session['recently_viewed']:
                request.session['recently_viewed'].remove(self.pk)
            
            recently_viewed_products=Product.objects.filter(pk__in=request.session['recently_viewed'])
            request.session['recently_viewed'].insert(0,self.pk)
            if len(request.session['recently_viewed'])> 5:
                request.session['recently_viewed'].pop()
        else:
            request.session['recently_viewed'] = [self.pk]
        request.session.modified= True
        return recently_viewed_products

    def get_option_attributes(self,option):
        return ProductOptionAttributes.objects.filter(product_option=option).order_by('priority').values('attribute_id','attribute__name').distinct()

    def get_option(self,request):
        options=self.options.all()
        if request:
            id=request.GET.get('option_id',-1)
            option=ProductOption.objects.filter(pk=id).first()
            if option:
                return option
        
            selected_filters = self.category._parse_request_filters(request)
            if selected_filters.get('size'):
                options = options.filter(attributes__attribute__name="Size",attributes__value__in=selected_filters.get('size'))

            if selected_filters.get('color'):
                options = options.filter(attributes__attribute__name="Color",attributes__value__in=selected_filters.get('color'))
        
        
        option = options.first()
        if option:
            return option
        return ProductOption.objects.get(pk=127)#default product option with no parent and not found images

    
    def userperm_add_to_cart(self):
        return True

    @property
    def label(self):
        return ""

    def url(self):
        return reverse('shop:productdetail',args=[self.slug,self.id])

    @property
    def edit_url(self):
        return reverse('shopadmin:editproduct',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deleteproduct',args=[self.id])
    
    @property
    def addproductoption_url(self):
        return reverse('shopadmin:addproductoptionproduct',args=[self.id])
    @property
    def addproductattribute_url(self):
        return reverse('shopadmin:addproductattributeproduct',args=[self.id])

def product_image_directory(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'upload/product/{0}/{1}'.format(instance.product_option.product_id, filename)


class ProductOption(BaseTechvinsModel):
    product = models.ForeignKey(Product,null=True,blank=True,on_delete=models.SET_NULL,related_name="options")
    sku = models.CharField(max_length=100,blank=True,null=True)
    quantity = models.IntegerField(default=0)
    priority = models.IntegerField(default=1)
    list_price = models.FloatField("MRP(Including Tax)", default=0)
    selling_price = models.FloatField("Selling Price(After Discounts,Including Tax)", default=0)
    history = HistoricalRecords()


    @property
    def out_of_stock(self):
        return self.quantity < 1

    @property
    def edit_url(self):
        return reverse('shopadmin:editproductoptionproduct',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deleteproductoptionproduct',args=[self.id])

    @property
    def addproductoptionattribute_url(self):
        return reverse('shopadmin:addproductoptionattributeproductoption',args=[self.id])

    @property
    def addproductoptionImage_url(self):
        return reverse('shopadmin:addproductoptionimageproductoption',args=[self.id])
    
    
    def decrease_quantity(self,quantity):
        '''
        when the product is added from cart to order, decrease the quantity
        :param quantity:
        :return:
        '''
        self.quantity -= quantity
        self.save()

    @property
    def price(self):
        return self.prices().get('selling_price')

    @property
    def get_discount_amount(self):
        return self.prices().get('discount_amount')
    
    @property
    def get_discount_percentage(self):
        return self.prices().get('discount_percentage')
    
    def in_stock(self):
        #TODO
        return True
        
    def image(self):
        return self.all_images().first().image
        # if self.images.all().exists():
        #     return self.images.first()

        # pm = ProductOptionImage.objects.filter(Q(product_option=self) | Q(product_option__product=self.product)).order_by('priority')
        # if pm.filter(is_common=True).exists():
        #     return pm.filter(is_common=True).first()
        # return pm.first()        
    
    def get_total_tax_rate(self):
        return self.product.tax_class.total_tax_rate if self.rate else 0

    def price_display(self, format=True):
        total = self.prices().get('list_price')
        return price_format(total) if format else total

    def all_images(self):
        all_images=ProductOptionImage.objects.filter(product_option=self).order_by('priority')
        if self.product.primary_attribute:
            primary_attribute_value=self.attributes.filter(attribute=self.product.primary_attribute).first().value
            all_images=all_images.filter(product_option__attributes__attribute=self.product.primary_attribute,product_option__attributes__value=primary_attribute_value)
                 
        return all_images.order_by('priority')
        
    @property
    def mrp(self):
        return self.prices().get('list_price')

    @property
    def name(self):
        #Product + hsn + fit n size + sku

        name = "{} ({})".format(self.product.name,self.subname)
        return name

    @property
    def subname(self):
        attributes = self.attributes.all()
        name = "{}/".format(self.product.hsn)
        name=""
        for a in attributes:
            name += " {}".format(a.value)
        return "{}/{}".format(name,self.sku)

    def get_product_attribute_values(self,attribute_id,option_only=False):
        duplicate_checker={}
        lst=[]

        attributes=ProductOptionAttributes.objects.filter(product_option__product=self.product,attribute_id=attribute_id).order_by('priority')
        if option_only:
            attr=Attribute.objects.get(name="Color")
            same_color_options=ProductOption.objects.filter(attributes__attribute=attr,attributes__value=self.color()).values_list('id')
            attributes = attributes.filter(product_option_id__in=same_color_options)

            # product_options=ProductOptionAttributes.objects.filter(\
            #     product_option=self).exclude(attribute_id=attribute_id).values_list('attribute_id','value')
            # query = Q()
            # for po in product_options:
            #     query &= Q(attribute_id=po[0],value=po[1])

            # pos=ProductOptionAttributes.objects.filter(query).values('product_option')
            # attributes = attributes.filter(product_option__in=pos)
        for p in attributes:
            if p.value in duplicate_checker:
                pass
            else:
                duplicate_checker[p.value]=p
                lst.append(p)
        return lst
    
    def color(self):
        attr=Attribute.objects.get(name="Color")
        return ProductOptionAttributes.objects.filter(product_option=self,attribute_id=attr.id).first().value
    
    def has_attribute_with_color(self,attr_id,val):
        attr=Attribute.objects.get(name="Color")
        same_color_options=ProductOption.objects.filter(attributes__attribute=attr,attributes__value=self.color()).values_list('id')
        return ProductOptionAttributes.objects.filter(product_option_id__in=same_color_options,attribute_id=attr_id,value=val).exists()

        ProductOptionAttributes.objects.filter(product_option=self,attribute_id=attr.id,value=self.color()).exists()
        x = ProductOptionAttributes.objects.filter(product_option=self,attribute_id=attr_id,value=val).exists()
        
        y = ProductOptionAttributes.objects.filter(product_option=self,attribute_id=attr.id,value=self.color()).exists()
        # print("x and y",x,y,attr_id,val)
        return x and y

        



    def __str__(self):
        return "{} Option: {}".format(self.product.name,self.id) if self.product else ""

    @property
    def attibute_summary(self):
        attributes = ""
        for a in self.attributes.all():
            attributes += "{}".format(a.value)
        return "{} - ".format(self.product.sku,attributes)


    def prices(self,selling_price=False):
        if not selling_price:
            selling_price = self.selling_price

        tax_bracket = self.product.tax_class.bracket(selling_price)
        d=dict()
        d['tax_bracket'] = tax_bracket
        d['list_price']=self.list_price
        d['selling_price']=self.selling_price
        d['sp_without_tax']=tax_bracket.total_amount(selling_price)
        d['discount_percentage']=int(((self.list_price - selling_price)/self.list_price)*100)
        d['discount_amount']= self.list_price - selling_price
        d['tax_bracket']=tax_bracket
        d['tax'] = d['selling_price'] - d['sp_without_tax']
        # print(d)
        return d

    def url(self):
        return "{}?option_id={}".format(self.product.url(),self.id)


class ProductAttributes(BaseTechvinsModel):
    '''
    THese for for static display only on product detail page
    '''
    product = models.ForeignKey(Product,blank=True,null=True,on_delete=models.CASCADE,related_name="attributes")
    name=models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    def __str__(self):
        return "{} : {}".format(self.name,self.value)

    @property
    def edit_url(self):
        return reverse('shopadmin:editproductattributeproduct',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deleteproductattributeproduct',args=[self.id])
    
class ProducOptionStatictAttributes(BaseTechvinsModel):
    '''
    THese for for static display only on product detail page
    '''
    product_option = models.ForeignKey(ProductOption,null=True,on_delete=models.CASCADE,related_name="static_attributes")
    name=models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    def __str__(self):
        return "{} : {}".format(self.name,self.value)


class ProductOptionAttributes(BaseTechvinsModel):
    product_option = models.ForeignKey(ProductOption,blank=True,null=True,on_delete=models.SET_NULL,related_name="attributes")
    attribute = models.ForeignKey(Attribute,on_delete=models.SET_NULL,null=True)
    value = models.CharField(max_length=120,blank=True,null=True)
    label = models.CharField(max_length=120,blank=True,null=True)
    priority = models.PositiveSmallIntegerField(default=99)
    history = HistoricalRecords()
    def __str__(self):
        return "{} Attribute:{}".format(self.product_option.product.name,self.attribute.name)
    
    @property
    def edit_url(self):
        return reverse('shopadmin:editproductoptionattributeproductoption',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deleteproductoptionattributeproductoption',args=[self.id])

class ProductOptionImage(BaseTechvinsModel):
    product_option = models.ForeignKey(ProductOption,blank=True,null=True,on_delete=models.SET_NULL,related_name="images")
    image = models.ImageField(upload_to=product_image_directory,null=True,blank=True,max_length=250)
    is_common = models.BooleanField("Is this image common for all options",default=False) 
    priority=models.IntegerField(default=1)
    
    def __str__(self):
        return "{} Image:{}".format(self.product_option.product.name,self.id) if self.product_option and self.product_option.product else ""

    @property
    def edit_url(self):
        return reverse('shopadmin:editproductoptionimageproductoption',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deleteproductoptionimageproductoption',args=[self.id])

    class Meta:
        ordering = ('priority',)
        
class Cart(BaseTechvinsModel):
    name=models.CharField(max_length=20,blank=True,default='')
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,null=True)
    status = models.PositiveSmallIntegerField(choices=choices.CartStatus.CHOICES,default=choices.CartStatus.FRESH)
    discount_label = models.CharField(max_length=120,blank=True,null=True)
    discount_amount = models.IntegerField(default=0)
    discount_category = models.ForeignKey(DiscountCategory,null=True,on_delete=models.SET_NULL)
    #static data, calculated stored
    total_without_tax = models.IntegerField(default=0)
    tax = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)

    shipping_address = models.ForeignKey(Address,null=True,blank=True,on_delete=models.SET_NULL,related_name="cart_with_shipping")
    billing_address = models.ForeignKey(Address,null=True,blank=True,on_delete=models.SET_NULL,related_name="cart_with_billing")

    shipping_tax_rate = models.IntegerField(default=0)
    shipping_amount = models.IntegerField(default=0)
    shipping_tax = models.IntegerField(default=0)
    discount_coupon = models.ForeignKey(DiscountCoupon,on_delete=models.SET_NULL,null=True,blank=True)
    history = HistoricalRecords()

    @property
    def detail_url(self):
        return reverse('shopadmin:cartdetail',args=[self.id])

    def can_checkout(self):
    
        if not self.cartproducts.count():
            return False, "Empty Cart"
        
        minimum_amount = int(Configuration.get('MINIMUM CART AMOUNT','5000'))
        if self.total_price < minimum_amount:
            return False, "Minimum cart amount should be Rs. {}".format(minimum_amount)
        return True,''

    @classmethod
    def get_cart(cls, request,create=True):
        user=request.user if request.user.is_authenticated else False
        cart = None
        cart_name = request.COOKIES.get(settings.SESSION_CART_NAME,False)

        #get cart by user
        if user:
            cart = cls.objects.filter(user=user).last()
            if cart is None and create:
                cart,created = cls.objects.get_or_create(user=user)

        #get cart by cookie value
        if cart_name:
            cart = Cart.objects.filter(name=cart_name).last()
            #set user in cart if logged in
            if cart and user:
                cart.user = user
                cart.save()

        #create new cart and set user if logged in
        if cart is None:
            if create:
                cart = Cart.objects.create(name=User.objects.make_random_password())
                if user:
                    cart.user=user
                    cart.save()
        return cart or Cart()


    def _save_partial_cart_product(self,product_id,product_option_id,quantity=1):
        '''
        Individual Cart product add before cart amount calculations
        '''
        cart_product, created = CartProducts.objects.get_or_create(cart=self, product_id=product_id,
                                                                   product_option_id=product_option_id)
        product_option = ProductOption.objects.get(pk=product_option_id)
        if not created:
            cart_product.quantity = cart_product.quantity + quantity
        else:
            cart_product.quantity = quantity

       

        if cart_product.quantity > 10:
            cart_product.quantity = 10
        if cart_product.quantity < 0:
            cart_product.quantity = 0
        

        cart_product.quantity = int(cart_product.quantity)
        prices = product_option.prices()
        cart_product.unit_price = prices.get('selling_price')
        


        cart_product.amount = int(cart_product.unit_price * cart_product.quantity)
        cart_product.total_without_tax =  prices.get('sp_without_tax') * cart_product.quantity# without tax and after product discount
        
        cart_product.discount_label = prices.get('discount_percentage')
        cart_product.discount_amount = cart_product.quantity * prices.get('discount_amount')
        # save the basic details of produt and calculate the new discount range
        
        tax_bracket = product_option.prices().get('tax_bracket')
        taxrate = tax_bracket.total_rate/100
        cart_product.tax = prices.get('tax') * cart_product.quantity #int(math.ceil(taxrate * cart_product.total_without_tax))
        # # cart_product.tax = round(product_option.get_tax() * cart_product.quantity,2)
        #
        cart_product.total_price = cart_product.total_without_tax+cart_product.tax
        cart_product.tax_bracket = tax_bracket


        cart_product.save()

        return  cart_product

    def reset_all_values(self):
        # reset all
        self.total_without_tax,  self.tax, self.total_price, self.discount_amount = 0, 0, 0, 0

    def _update_cart_amount_from_products(self):
        self.reset_all_values()
        self._check_shipping()  
        # print("Total price with add cart product",self.total_price,self.discount_amount)
        #calculate again
        for cp in self.cartproducts.all():
                
            self.total_without_tax += cp.total_without_tax
            self.tax += cp.tax
            self.total_price += cp.total_price
            self.discount_amount += cp.discount_amount
            self.discount_label = "Discount({}%)".format(cp.discount_label)

        
        
        self._check_shipping()  
        self.tax += self.shipping_tax
        self.total_price += self.shipping_amount + self.shipping_tax

        self._check_discount_coupon()        
        self.save()

        if self.cartproducts.all().count() < 1:
            self.clean_this()

    def _check_discount_coupon(self):
        if  self.discount_coupon and self.total_without_tax >= self.discount_coupon.min_cart_amount:
            discount=self.discount_coupon.get_discount(self.total_without_tax)
            self.total_price -= discount
            self.discount_amount += discount
        else:
            self.discount_coupon = None

    def is_eligible_to_cart(self,po):
        #product option quantity zero, cannot be added to cart
        if po and po.quantity > 0 and Configuration.get("Shopping Enabled(YES/NO)","NO") == "YES":
            pass
        else:
            raise Exception("Product Cannot be added to cart!")
        #ends here, product option quantity zero, cannot be added to cart

    def _before_add_to_cart_hook(self,po):
        pass

    def add_product(self,product_id,product_option_id,quantity=1):
        po=ProductOption.objects.filter(pk=product_option_id).first()        

        self._before_add_to_cart_hook(po)   

        cart_product = self._save_partial_cart_product(product_id,product_option_id,quantity)

        discount_category = DiscountCategory.get_for_cart(self)
        self.discount_category = discount_category
        self.save()

        product_option = po

        # cart_product.save()

        #if category found, calculate for all products
        if discount_category:
            for cp in self.cartproducts.all():
                cp.discount_label = discount_category.value + product_option.discount_percentage
                cp.discount_amount += discount_category.get_discount(cp.total_without_tax)
                
                cp.total_without_tax  -= cp.discount_amount

                cp.save()
                # self.discount_amount += cp.discount_amount
                # self.discount_label = cart_product.discount_label

        cart_product.refresh_from_db()        


        # cart_product.total_price -= cart_product.total_price - discount_category.get_discount(cart_product.total_price)
        #
        tax_bracket = product_option.prices().get('tax_bracket')
        taxrate = tax_bracket.total_rate/100
        prices = product_option.prices()
        cart_product.tax =  prices.get('tax') * cart_product.quantity #int(math.ceil(taxrate * cart_product.total_without_tax))
        # # cart_product.tax = round(product_option.get_tax() * cart_product.quantity,2)
        #
        cart_product.total_price = cart_product.total_without_tax+cart_product.tax
        cart_product.tax_bracket = tax_bracket
        cart_product.save()
        
        self._update_cart_amount_from_products()

        
    def _check_shipping(self):
        total =  self.total_price_with_tax(formatted=False)
        free_shipping_beyond = int(Configuration.get('CHECKOUT_FREE_SHIPPING_BEYOND','1499'))
        
        
        if total < free_shipping_beyond and self.cartproducts.all().count():
            shipping_charge = int(Configuration.get('CHECKOUT_SHIPPING_CHARGES','100'))
            self.shipping_tax_rate = self._get_highest_tax_rate()

            shipping_rate = int(shipping_charge*(shipping_charge/(shipping_charge+self.shipping_tax_rate)))
            tax_amount = shipping_charge - shipping_rate
            self.shipping_tax = tax_amount
            self.shipping_amount = shipping_rate
        else:
            self.shipping_amount = 0
            self.shipping_tax_rate = 0
            self.shipping_tax = 0
        self.save()

    def _get_highest_tax_rate(self):
        return self.cartproducts.all().aggregate(max_rate=Max('tax_bracket__igst_rate'))['max_rate']
        
    def _check_update_discount(self):
        self.discount_label,self.discount_amount = '',0

        discount_category = DiscountCategory.get_for_cart(self)
        if discount_category:
            self.discount_category = discount_category
            self.discount_amount = discount_category.get_discount(self.total_without_tax)
            self.discount_label = discount_category.get_label()
            # self._update_individual_product_discount()
        self.save()

    def _update_individual_product_discount(self):
        total_cart_value= self.total_price_without_tax(formatted=False)
        for cartproduct in self.cartproducts.all():
            product_total = cartproduct.quantity * cartproduct.product_option.price
            cartproduct.discount_label = self.discount_category.value

            cartproduct.discount_amount = round(((self.discount_amount/total_cart_value)*product_total),2)
            cartproduct.save()

    @classmethod
    def breadcrumb(cls):
        title = "My Cart"
        l = [
            {
            'title': title,
            'text': title,
            'url': ''
            }
        ]
        return build_breadcrumb(l)

    @classmethod
    def common_context(cls):
        title = "My Cart"
        ctx = {}
        ctx['html_head'] = build_html_head(title=title,description=title)
        ctx['breadcrumb'] = Cart.breadcrumb()
        return ctx

    def remove_product(self,product_id,product_option_id):
        self.cartproducts.filter(product_id=product_id,product_option_id=product_option_id).delete()
        self._update_cart_amount_from_products()

    def product_count(self):
        return self.cartproducts.all().count()


    def total_price_with_tax(self,formatted=True):
        total = 0.0
        for cartproduct in self.cartproducts.all():
                total += cartproduct.total_price

        if self.discount_coupon:
            total -= self.discount_coupon.get_discount(self.total_without_tax)  
        return price_format(total) if formatted else total

    def total_price_without_tax(self,formatted=True):
        total = 0.0
        for cartproduct in self.cartproducts.all():
            total += cartproduct.total_without_tax
        if self.discount_coupon:
            total -= self.discount_coupon.get_discount(self.total_without_tax)
        return price_format(total) if formatted else total

    # def total_price(self,final=True,formatted=True):
    #     total = 0.0
    #     for cartproduct in self.cartproducts.all():
    #         total += cartproduct.quantity * cartproduct.product_option.price_display(format=False)
    #
    #     if final:
    #         total -= self.discount_amount
    #
    #     return price_format(total) if formatted else total


    def is_eligible_for_checkout(self):
        return self.cartproducts.all().count() > 0

    def place_order(self):
        #create order
        order,created = Order.objects.get_or_create(cart=self,order_status=choices.OrderStatus.PENDING,\
            name=self.shipping_address.name,email=self.shipping_address.email,mobile=self.shipping_address.mobile) 
        order.user = self.shipping_address.user
        order.name=self.shipping_address.name
        order.email=self.shipping_address.email
        order.mobile=self.shipping_address.mobile
        order.discount_amount =self.discount_amount
        order.discount_label = self.discount_label
        order.total_without_tax = self.total_without_tax
        order.tax = self.tax
        order.total_price = self.total_price
        order.shipping_amount = self.shipping_amount
        order.shipping_tax_rate = self.shipping_tax_rate
        order.shipping_tax = self.shipping_tax
        #updated to be only on payment success
        # order.invoice_number = get_invoice_number()
        order.save()

        #update address in order
        # address = self.user.get_address(only_existing=True)
        # if not address:
        #     raise Exception("Address should be available for user")

        order.update_address(self.shipping_address,self.billing_address)

        #add products in order from cart
        for cp in self.cartproducts.all():
            order.add_product_option(cp)

        self.clean_this()

        
        
        return order
   
    def clean_this(self):
         #since same cart is used again and agin for one user, need to keep clean
        self.cartproducts.all().delete()
        self.reset_all_values()
        self.delete()
        
    def can_apply_coupon(self):
        coupon = DiscountCoupon.get_eligible_coupons(self)
        if coupon:
            return True
        return False
    
    
    def get_available_discount_coupons(self):
        return DiscountCoupon.get_eligible_coupons(self)
    
    def update_cart_discount_amount(self):
        self._update_cart_amount_from_products()
            
    def is_first_time_order(self):
        if Order.objects.filter(user=self.user,payment_status=choices.OrderPaymentStatus.APPROVED):
            return False
        return True
        

class CartProducts(BaseTechvinsModel):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="cartproducts")
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    product_option = models.ForeignKey(ProductOption,on_delete=models.CASCADE)
    tax_bracket = models.ForeignKey(TaxClassBracket,null=True,blank=True,on_delete=models.SET_NULL)
    
    history = HistoricalRecords()

    quantity=models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    unit_price = models.IntegerField('individual item rate',default=0)
    amount = models.IntegerField('individual rate * quantity', default=0)

    discount_label = models.CharField('discount percentage',max_length=200,blank=True,null=True)
    discount_amount = models.IntegerField('discount amount',default=0)

    total_without_tax = models.IntegerField('total without tax',default=0)

    tax = models.IntegerField(default=0)
    total_price = models.IntegerField("total without tax + tax",default=0)
    
    @property
    def detail_url(self):
        return reverse('shopadmin:cartproductdetail',args=[self.id])
   
    def price_display(self, format=True):
        return price_format(self.total_price) if format else self.total_price

class Order(BaseTechvinsModel):
    cart = models.ForeignKey(Cart,null=True,on_delete=models.SET_NULL)
    user = models.ForeignKey(get_user_model(),on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=220)
    email = models.CharField(max_length=255)
    mobile = models.BigIntegerField()
    invoice_number = models.CharField(max_length=20,blank=True,null=True)
    discount_label = models.CharField(max_length=200,blank=True, null=True)
    discount_amount = models.IntegerField(default=0)
    total_without_tax = models.IntegerField(default=0)
    tax = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    
    shipping_address= models.CharField(max_length=512,blank=True,null=True)
    #foreign key to calculate shipping in future
    shipping_pincode = models.ForeignKey(Pincode,blank=True,null=True,on_delete=models.SET_NULL,related_name="order_with_shipping")
    
    
    billing_address= models.CharField(max_length=512,blank=True,null=True)
    billing_pincode = models.ForeignKey(Pincode,blank=True,null=True,on_delete=models.SET_NULL,related_name="order_with_billing")
    
    
    shipping_tax_rate = models.IntegerField(default=0)
    shipping_amount = models.IntegerField(default=0)
    shipping_tax = models.IntegerField(default=0)
    
   
    # total = models.FloatField(default=0)
    
    order_status = models.PositiveSmallIntegerField(choices=choices.OrderStatus.CHOICES,default=choices.OrderStatus.PENDING)
    payment_status = models.PositiveSmallIntegerField(choices=choices.OrderPaymentStatus.CHOICES,default=choices.OrderStatus.PENDING)
    # shipment_status = models.PositiveSmallIntegerField(choices=choices.ShipmentStatus.CHOICES,default=choices.ShipmentStatus.NONE)
    history = HistoricalRecords()

    @property
    def edit_url(self):
        return reverse('shopadmin:editorder',args=[self.id])

    @property
    def add_ordershipment_url(self):
        return reverse('shopadmin:addordershipmentorder',args=[self.id])

    @property
    def add_ordershipmentattribute_url(self):
        return reverse('shopadmin:ordershipmentattributeorder',args=[self.id])
    
    @property
    def invoice_date(self):
        return self.created

    def is_igst_applicable(self):
        return self.shipping_pincode.city_state.state_name !=  "Rajasthan"
    
    def is_cancellable(self):
        return False
        return self.order_status in [0,10,20]
        
    @classmethod
    def shipment_ready_orders(cls):
        return Order.objects.filter(order_status=choices.OrderStatus.PROCESSING).order_by('-id')
        
    @property
    def retry_payment_url(self):
        if self.id:
            return reverse('shop:paymentretry',kwargs={'order_id':signing.dumps(self.id)})
        return ""


    def shipping_tax_calculated(self):
        d={}
        shipping_charge= self.shipping_amount
        tax_rate = self.shipping_tax_rate
        shipping_rate = int(shipping_charge*(shipping_charge/(shipping_charge+tax_rate)))
        tax_amount = shipping_charge - shipping_rate
        d['shipping_rate'] = shipping_rate
        d['tax_amount'] = tax_amount
        if self.shipping_pincode.city_state.state_name ==  "Rajasthan":
            d['igst'] =0,0
            d['cgst'] = round(tax_rate/2,2),round(tax_amount/2,2)
            d['sgst'] = round(tax_rate/2,2),round(tax_amount/2,2)
        else:
            d['igst'] = tax_rate,tax_amount
            d['cgst'] = 0,0
            d['sgst'] = 0,0
        # print(d)
        return d


    def update_address(self,shipping_address,billing_address):
        self.shipping_address = shipping_address.one_line()
        self.shipping_pincode = shipping_address.pincode
        self.billing_address = billing_address.one_line()
        self.billing_pincode = billing_address.pincode
        self.save()

    def add_product_option(self,cart_product_option):
        product_option = cart_product_option.product_option
        op = OrderProducts.objects.filter(order=self,product=product_option.product,product_option = product_option).first()
        if op:
            op.manufacturer = product_option.product.manufacturer.name
            op.name = product_option.product.name
            op.option_name = product_option.name
            op.tax_bracket = cart_product_option.tax_bracket
            
            op.quantity = cart_product_option.quantity
            op.unit_price = cart_product_option.unit_price
            op.amount = cart_product_option.amount
            
            op.discount_label = cart_product_option.discount_label
            op.discount_amount = cart_product_option.discount_amount

            op.total_without_tax = cart_product_option.total_without_tax
            op.tax = cart_product_option.tax
            op.total_price = cart_product_option.total_price
            
            op.save()
        else:
            d={}
            d['order']=self
            d['product']=product_option.product
            d['product_option'] = product_option
            d['manufacturer'] = product_option.product.manufacturer.name
            d['name'] = product_option.product.name
            d['option_name'] = product_option.name
            d['tax_bracket_id'] = cart_product_option.tax_bracket_id
            
            d['quantity'] = cart_product_option.quantity
            d['unit_price'] = cart_product_option.unit_price
            d['amount'] = cart_product_option.amount
            
            d['discount_label'] = cart_product_option.discount_label
            d['discount_amount'] = cart_product_option.discount_amount

            d['total_without_tax'] = cart_product_option.total_without_tax
            d['tax'] = cart_product_option.tax
            d['total_price'] = cart_product_option.total_price
            
            OrderProducts.objects.create(**d)

        #decrease the product quantity
        product_option.decrease_quantity(cart_product_option.quantity)



    def invoice_link(self):
        if self.payment_status == choices.OrderPaymentStatus.APPROVED:
            return "{}?order_id={}".format(reverse('users:invoice'),self.id)
        return ''

    def get_order_id(self):
        rsvc = RazorpayService()
        order_receipt = "order_{}".format(self.id)
        return rsvc.create_order(order_amount=self.get_total_amount(),order_receipt = order_receipt)
        # return "order_asdf{}".format(self.id)

    def get_payment_user_info(self):
        d={}
        d['name']=self.name
        d['email'] = self.email
        d['contact'] =self.mobile
        return d

    def get_total_amount(self):
        if settings.DEBUG:
             return 100 #paise
        return self.total_price * 100

    def get_payment_info(self):
        d={}
        d['key'] = settings.RAZORPAY_KEY
        d['amount'] = self.get_total_amount()
        d['currency'] = "INR"
        d['name'] = Configuration.get('SITE_NAME','AADHARA')
        d['description'] = "Order #{}".format(self.id) 
        d['image'] = img_tag(size="100/100",src=settings.LOGO_URL,url_only=True)
        if not settings.DEBUG:
            d['order_id'] = self.get_order_id()
        d['order_id'] = self.get_order_id()
        # d['handler'] = 
        d['prefill'] = self.get_payment_user_info()
        d['notes']={'django_order_id':self.id,'mobile':self.mobile,'email':self.email,'name':self.name}
        return d

    def add_payment(self, **kwargs):
        op = OrderPayment()
        op.order = self
        op.gateway = kwargs.get('gateway')
        op.gateway_order_id = kwargs.get('gateway_order_id')
        op.gateway_payment_id = kwargs.get('gateway_payment_id')
        op.gateway_signature = kwargs.get('gateway_signature')
        op.save() 
        op.update_status()

    def is_paid_successfully(self):
        op = OrderPayment.objects.filter(order=self).last()
        if op:
            if op.is_success and self.payment_status != choices.OrderPaymentStatus.APPROVED:
                self._paid_successfully()            
            return op.is_success
        return False
        
    def _paid_successfully(self):
        self.payment_status = choices.OrderPaymentStatus.APPROVED 
        self.order_status = choices.OrderStatus.PLACED
        self.save()


    @classmethod
    def common_context(cls):
        title = "My Order"
        ctx = {}
        ctx['html_head'] = build_html_head(title=title,description=title)
        ctx['breadcrumb'] = Cart.breadcrumb()
        return ctx

    def get_shipping_address(self):
        return "{} - {}".format(self.shipping_address,self.shipping_pincode.pincode)
        
    def get_supply_state_info(self):

        # import web_pdb;
        # web_pdb.set_trace()
        return "{} ({})".format(self.shipping_pincode.city_state.state_name,self.shipping_pincode.city_state.get_gst_code())



    def _get_products_value_sum(self,value):
        return OrderProducts.objects.filter(order=self).aggregate(sum=Sum(value))['sum']

    def get_taxable(self):
        return self._get_products_value_sum('price')

    def get_taxes(self):
        return self._get_products_value_sum('tax')

    def get_total(self,formatted=True):
        total = 0
        for p in self.products.all():
            total += p.total_cost(formatted=False)
        total = round(total,2)
        return price_format(total) if formatted else total

    def total_products(self):
        return  self._get_products_value_sum('quantity')

    def get_total_weight(self,formatted=True):
        weight_gram = 0
        for product in self.products.all():
            weight_gram += product.get_weight()
        return "{} grams".format( weight_gram) if formatted else weight_gram


    def tax_calculated(self,formatted=True):
        tax=0
        
        for p in self.products.all():
            tax += p.tax

        return price_format(tax) if formatted else tax

    @property
    def payment(self):
        return  self.payments.all().last()

    @property
    def shipment(self):
        return self.shipments.all().last()
    
    def _get_shipping_attribute(self,type, value_only=True):
        attr=self.shipment_attributes.all().filter(key=type).last()
        if attr:
            return attr.value if value_only else attr
        return '-'

    def shipping_length(self):
        return self._get_shipping_attribute(choices.ShipmentProviderAttributes.LENGTH)
    
    def shipping_width(self):
        return self._get_shipping_attribute(choices.ShipmentProviderAttributes.WIDTH)
    
    def shipping_height(self):
        return self._get_shipping_attribute(choices.ShipmentProviderAttributes.HEIGHT)
    
    def shipping_weight(self):
        return self._get_shipping_attribute(choices.ShipmentProviderAttributes.WEIGHT)
    
    def shipping_awb_no(self):
        return self._get_shipping_attribute(choices.ShipmentProviderAttributes.AWB_NO)
 
    def shipping_courier_name(self):
        return self._get_shipping_attribute(choices.ShipmentProviderAttributes.COURIER_NAME)

class OrderShipment(BaseTechvinsModel):
    order = models.ForeignKey(Order,blank=True, on_delete=models.CASCADE, related_name="shipments")
    shipment_company = models.CharField(max_length=200,blank=True,null=True)
    shipped_on = models.DateField(blank=True,null=True)
    tracking_no = models.CharField(max_length=200,blank=True,null=True)

    def __str__(self):
        return "{}:{} on {}".format(self.order_id,self.shipment_company,self.shipment_company)

    def save(self, *args, **kwargs):
        super(OrderShipment, self).save(*args, **kwargs)
        order =self.order
        if not order.invoice_number:
            order.invoice_number = get_invoice_number()
            order.save()

    @property
    def edit_url(self):
        return reverse('shopadmin:editordershipmentorder',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deleteordershipment',args=[self.id])

class OrderShipmentAttributes(BaseTechvinsModel):
    order = models.ForeignKey(Order, blank=True,on_delete=models.CASCADE, related_name="shipment_attributes")
    key = models.PositiveSmallIntegerField(choices=choices.ShipmentProviderAttributes.CHOICES)
    value = models.CharField(max_length=300)

    @property
    def edit_url(self):
        return reverse('shopadmin:editordershipmentattributeorder',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deleteordershipmentattribute',args=[self.id])

class OrderAddress(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="addresses")
    name = models.CharField(max_length=255)
    street = models.CharField(max_length=512)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=6)

    def complete(self):
        return "{}, {}, {}, {}, {}-{}".format(name,street,city,state,pincode)

class OrderProducts(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="products")
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    product_option = models.ForeignKey(ProductOption,on_delete=models.SET_NULL,null=True)
    tax_bracket = models.ForeignKey(TaxClassBracket,null=True,blank=True,on_delete=models.SET_NULL)
    manufacturer = models.CharField(max_length=512,blank=True,null=True)
    name = models.CharField(max_length=512,blank=True,null=True)
    option_name = models.CharField(max_length=512,blank=True,null=True)
    
    quantity = models.IntegerField()
    unit_price = models.IntegerField()
    amount = models.IntegerField('individual rate * quantity', default=0)

    discount_label = models.CharField(max_length=200,blank=True,null=True)
    discount_amount = models.IntegerField(default=0)
    


    total_without_tax = models.IntegerField(default=0)

    tax = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    
   
    history = HistoricalRecords()


    def total_price_display(self):
        return "Rs. {}".format(self.total_price)

    def get_weight(self):
        return self.product.weight_gram * self.quantity

    # def total_tax(self):
    #     return self.tax_calculated()['total']

    def total_cost(self,formatted=True):
        return price_format(self.total_price) if formatted else self.total_price

    def price_display(self):
        return price_format(self.price)

    # @property
    # def discount(self):
    #     return 0
    #
    # def discount_amount(self):
    #     return 0

    def tax_calculated(self):
        d={}
        if self.order.shipping_pincode.city_state.state_name ==  "Rajasthan":
            d = self._add_tax(d,'igst',0)
            d = self._add_tax(d, 'cgst', self.tax_bracket.cgst_rate)
            d = self._add_tax(d, 'sgst', self.tax_bracket.sgst_rate)
        else:
            d = self._add_tax(d, 'igst', self.tax_bracket.igst_rate)
            d = self._add_tax(d, 'cgst', 0)
            d = self._add_tax(d, 'sgst', 0)
        return d

    def _add_tax(self,d,name,percent):
        amount = round(((self.total_without_tax * percent)/100),2)
        d[name] = percent,amount
        return d

class OrderPayment(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="payments")
    gateway = models.SmallIntegerField(choices=choices.GatewayChoices.CHOICES)
    gateway_order_id = models.CharField(max_length=120,blank=True,null=True)
    gateway_payment_id = models.CharField(max_length=120,blank=True,null=True)
    gateway_signature = models.CharField("The transaction signature",max_length=120,blank=True,null=True)
    is_success = models.SmallIntegerField(choices=choices.YesNoChoices.CHOICES,default=choices.YesNoChoices.NO)
    history = HistoricalRecords()
    
    def update_status(self):
        if self.gateway == choices.GatewayChoices.RAZORPAY:
            rsvc = RazorpayService()
            status = rsvc.verify_payment(self)
            if status:
                self.is_success = choices.YesNoChoices.YES
                self.order.order_status = choices.OrderStatus.PLACED
                self.order.invoice_number = get_invoice_number()
                self.order.save()
                self.save()
                if not settings.DEBUG:
                    from shop.tasks import order_placed_task
                    order_placed_task.delay(self.order.id) 



class Wishlist(BaseTechvinsModel):
    user = models.ForeignKey('users.User',on_delete=models.CASCADE)
    product_option=models.ForeignKey(ProductOption,on_delete=models.CASCADE)
