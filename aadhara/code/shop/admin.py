from django.contrib import admin
from django import forms
from .models import (CartProducts, Manufacturer,Category,Attribute,Product,ProductOptionImage,ProductOption,ProductOptionAttributes,
                     TaxClass,TaxClassBracket,Order,OrderProducts,OrderPayment,OrderShipment,DiscountCategory,
                     ProductAttributes,Wishlist,HomepageCategory,Cart,OrderShipmentAttributes,DiscountCoupon)
from ckeditor.widgets import CKEditorWidget
from django.templatetags.static import static
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from django.utils.safestring import mark_safe
from core import choices

# Register your models here.

def mark_disabled(modeladmin, request, queryset):
    queryset.update(status=0)
mark_disabled.short_description = "Mark selected products as disabled"

def mark_processing(modeladmin, request, queryset):
    queryset.update(order_status=choices.OrderStatus.PROCESSING)
mark_processing.short_description = "Mark selected orders as Processing"

def mark_enabled(modeladmin, request, queryset):
    queryset.update(status=1)
mark_enabled.short_description = "Mark selected products as enabled"

# admin.site.disable_action('delete_selected')


class ProductOptionImageInline(NestedStackedInline):
    model = ProductOptionImage
    extra = 0
    fields= ['image','priority']

class ProductOptionForm(forms.ModelForm):

    def is_multipart(self):
        return True

    class Meta:
        model = ProductOption
        save_on_top=True
        fields = ['list_price','quantity']

class ProductOptionAttributesInline(NestedStackedInline):
    model = ProductOptionAttributes
    extra = 0
    fields= ['attribute','value','label']
    


class ProductOptionInline(NestedStackedInline):
    '''
    ref: https://djangotricks.blogspot.com/2016/12/django-administration-inlines-for-inlines.html
    '''
    model = ProductOption
    extra = 0
    form = ProductOptionForm
    readonly_fields=['gst_amount','gst_rate','initial_rate',
                     'discount_amount','discounted_rate','discount_rate','final_selling_price',
                     'invoice_selling_price','discount_percentage']
    fields = [('list_price', 'gst_rate', 'gst_amount'), ('rate_duplicate', 'discount_percentage', 'discount_amount'),
              ('selling_price_duplicate'), 'quantity']

    fields = [('list_price','selling_price', 'gst_rate', 'gst_amount', ),
              ('discount_percentage','discount_amount'),
              ('invoice_selling_price'),
              ('quantity','sku')
              ]

    # fields= [('list_price','discount_percentage'),('discount_amount','gst_tax'),('list_price'),'quantity']
    inlines = [ProductOptionAttributesInline,ProductOptionImageInline]

    
    def discount_percentage(self,obj):
        return obj.prices().get('discount_percentage')


    def invoice_selling_price(self,obj):
        return obj.prices().get('list_price')

    
    def mrp(self,obj):
        return obj.prices().get('initial_mrp')

    def gst_rate(self,obj):
        return obj.prices().get('tax_bracket').total_rate

    def gst_amount(self,obj):
        return obj.prices().get('tax')

    
    
    def initial_rate(self,obj):
        return obj.prices().get('initial_rate')

    def discount_amount(self,obj):
        return obj.prices().get('discount_amount')

    def discounted_rate(self,obj):
        return self.discount_rate(obj)

    def discount_rate(self,obj):
        return obj.prices().get('discount_rate')

    def final_selling_price(self,obj):
        return self.mrp(obj)


class ProductAttributesInline(NestedStackedInline):
    '''
    ref: https://djangotricks.blogspot.com/2016/12/django-administration-inlines-for-inlines.html
    '''
    model = ProductAttributes
    extra = 3
    fields= ['name','value']


class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
        
    class Meta:
        model = Product
        fields = ['name','summary','manufacturer','primary_category','categories','description','sku','hsn','location','weight_gram','tax_class','status','return_days','youtube_link','primary_attribute']
    

class ProductAdmin(NestedModelAdmin):
    form = ProductAdminForm
    date_hierarchy = 'created'
    list_display = ['id', 'image_tag','name','manufacturer','sku','status','tax_class']
    sortable_by=['id', 'name','sku','status','tax_class']
    ordering = ['-modified']
    # list_editable=['name','email']
    list_filter = ('status','created','tax_class','primary_category')
    search_fields=['id','name','sku','hsn']
    actions = [mark_disabled,mark_enabled]
    inlines = [ProductOptionInline,ProductAttributesInline]
    list_display_links = ['id', 'name']

    save_on_top=True



    class Media:   
        css = {
             'all': (static('admin/override.css'),)
        }

class ManufacturerAdmin(admin.ModelAdmin):
	fields=['name']
	# date_hierarchy=['created']
	list_filter=['id','name']

class CategoryAdmin(admin.ModelAdmin):
    fields=['name','parent','shipping_and_returns','size_chart','placeholder','priority']
    list_display=['id','name','parent','priority']
    sortable_by=['id','name','priority','parent']
    list_display_links = ['id', 'name']

    # date_hierarchy=['created']
    # list_filter=['id','name','parent']

class TaxClassBracketAdmin(admin.TabularInline):
    model = TaxClassBracket
    fields=['min_rate','max_rate','cgst_rate','sgst_rate','igst_rate']
    # readonly_fields=fields
    extra=1



class TaxClassAdmin(admin.ModelAdmin):
    inlines = [
        TaxClassBracketAdmin
    ]

    fields=['name','description']
    search_fields = ['id', 'name']
    list_display=['id','name','description']
    list_display_links = ['id', 'name']

class OrderProductsInline(admin.TabularInline):
    model = OrderProducts
    fields=['name','option_name','manufacturer','quantity','unit_price','tax','total_price']
    readonly_fields=fields


    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    fields=['gateway','gateway_order_id','gateway_payment_id','is_success']
    readonly_fields=fields


    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class OrderShipmentInline(admin.TabularInline):
    model = OrderShipment
    fields=['shipment_company','shipped_on','tracking_no']
    # readonly_fields=fields
    extra=1

class OrderShipmentAttributesInline(admin.TabularInline):
    model = OrderShipmentAttributes
    fields=['key','value']
    # readonly_fields=fields
    extra=1

class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderProductsInline,OrderPaymentInline,OrderShipmentInline,OrderShipmentAttributesInline
    ]
    # def get_queryset(self, request):
    #     qs = super(OrderAdmin, self).get_queryset(request)
    #     return qs.filter(payment_status=choices.OrderPaymentStatus.APPROVED)

    def products(self,obj):
        return obj.total_products()

    def amount(self,obj):
        return obj.get_total()

    def taxes(self,obj):
        return obj.tax_calculated()
    
    
    def invoice(self,obj):
        return mark_safe("<a href='{link}' target=_BLANK>{inv_no}</a>".format(link=obj.invoice_link(),inv_no=obj.invoice_number))
    date_hierarchy = 'created'

    readonly_fields =['user','created','invoice','payment_status','shipping_pincode','amount','taxes']
    fields = ['user', 'name', 'email', 'mobile','shipping_address','shipping_pincode','order_status','payment_status','amount','taxes']
    search_fields = ['invoice_number', 'name','email','mobile','user_id']
    list_filter=['payment_status','order_status']
    list_display = ['id', 'name', 'user_id','email', 'mobile', 'created','products','amount','taxes','payment_status','order_status','invoice']
    list_display_links = ['id', 'name']
    actions = [mark_processing]

    
class DiscountCategoryAdmin(admin.ModelAdmin):
    readonly_fields=['created']
    fields=['created','name','category_type','min_cart_amount','type','value','start_date_time','end_date_time']
    search_fields = ['id', 'name']
    list_display=['id','name','category_type','min_cart_amount','type','value']
    list_display_links = ['id', 'name']


class AttributeAdmin(admin.ModelAdmin):
    readonly_fields=['created']
    fields=['name']
    search_fields = ['id', 'name']
    list_display=['id','name']
    list_display_links = ['id', 'name']

class HomepageCategoryAdmin(admin.ModelAdmin):
    # readonly_fields = ('name',)
    fields = ['category','title','subtitle','button_text','enabled','priority','image']
    date_hierarchy = 'created'
    list_display = ['id', 'category','title','button_text','priority','enabled','created','modified']
    sortable_by=['id', 'category','created','priority']
    ordering = ['category']
    # list_editable=['category','email']
    list_filter = ('modified','created')
    search_fields=['category','title']
    list_display_links=['id','category']

      
class DiscountCouponAdmin(admin.ModelAdmin):
    fields = ['code','name','coupon_type','start_date','end_date','min_cart_amount','discount_value','discount_type','max_discount','summary','discount_image']
    date_hierarchy='created'
    list_display=['id','code','name','start_date','end_date','min_cart_amount','discount_value','discount_type','max_discount']
    sortable_by=['id','created','discount_value','discount_type','max_discount']
    ordering=['created']
    list_filter =['max_discount','discount_value','discount_type','created']
    search_fields =['start_date','code','name']
    list_display_links=['id','code','name']


admin.site.register(DiscountCoupon,DiscountCouponAdmin)
admin.site.register(Manufacturer,ManufacturerAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Attribute,AttributeAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(TaxClass,TaxClassAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(DiscountCategory,DiscountCategoryAdmin)
admin.site.register(Wishlist)
admin.site.register(HomepageCategory,HomepageCategoryAdmin)
admin.site.register(Cart)
admin.site.register(CartProducts)
admin.site.register(TaxClassBracket)
admin.site.register(ProductOption)
admin.site.register(ProductOptionImage)
admin.site.register(ProductOptionAttributes)
admin.site.register(ProductAttributes)

