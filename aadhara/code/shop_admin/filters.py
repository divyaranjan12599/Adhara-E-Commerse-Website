import django_filters
from core.models import CityState, Configuration, ContactUs, GalleryImage, HomepageSlider, Pincode,NewsletterSubscriber, Promotion, StaticPage
from shop.models import Attribute, Cart, CartProducts, Category, DiscountCategory, DiscountCoupon, HomepageCategory, Order, Product, TaxClass,Manufacturer, Wishlist

class BaseFilter(django_filters.FilterSet):
    def __init__(self,data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        for field_name,field in self.filters.items():
            if field.field.widget.attrs.get('class'):
                field.field.widget.attrs['class'] += 'form-control'
            else:
                field.field.widget.attrs['class'] = 'form-control'  
                
class CityStateFilter(BaseFilter):
    class Meta:
        model = CityState
        fields = ['name','type','parent']

class PincodeFilter(BaseFilter):
    class Meta:
        model = Pincode
        fields=['pincode','city_state']
        
class GalleryImageFilter(BaseFilter):
    class Meta:
        model = GalleryImage
        fields=['title','priority']

class ContactUsFilter(BaseFilter):
    class Meta:
        model = ContactUs
        fields =['name','mobile']
        
class ConfigurationFilter(BaseFilter):
    class Meta:
        model = Configuration
        fields = ['key','value']
            
class HomepagesliderFilter(BaseFilter):
    class Meta:
        model = HomepageSlider
        fields = ['name','priority','title']
        
class NewsletterSubscriberFilter(BaseFilter):
    class Meta:
        model = NewsletterSubscriber
        fields=['id']
        
class PromotionFilter(BaseFilter):
    class Meta:
        model = Promotion
        fields = ['name']
        
class StaticPageFilter(BaseFilter):
    class Meta:
        model = StaticPage
        fields = ['title']  
        
class AttributeFilter(BaseFilter):
    class Meta:
        model = Attribute
        fields = ['name']
        
class CategoryFilter(BaseFilter):
    class Meta:
        model = Category
        fields = ['name','parent','priority']        
        
class TaxClassFilter(BaseFilter):
    class Meta:
        model = TaxClass
        fields = ['name']

class ProductFilter(BaseFilter):
    class Meta:
        model = Product
        fields = ['name','primary_category','hsn','sku','status']

class DiscountCategoryFilter(BaseFilter):
    class Meta:
        model = DiscountCategory
        fields = ['name','category_type','min_cart_amount','type','value','start_date_time','end_date_time']
        
class HomepageCategoryFilter(BaseFilter):
    class Meta:
        model = HomepageCategory
        fields = ['category','title','enabled','priority']
        
class ManuFacturerFilter(BaseFilter):
    class Meta:
        model = Manufacturer
        fields = ['name']
        
class DiscountCouponFilter(BaseFilter):
    class Meta:
        model = DiscountCoupon
        fields = ['code','start_date','end_date','discount_type','coupon_type']
        
class CartFilter(BaseFilter):
    class Meta:
        model = Cart
        fields = ['user','status','discount_amount','total_price']
        
class WishlistFilter(BaseFilter):
    class Meta:
        model = Wishlist
        fields =['user']
        
class CartProductFilter(BaseFilter):
    class Meta:
        model = CartProducts
        fields = ['cart','product','product_option','total_price']
        
class OrderFilter(BaseFilter):
    class Meta:
        model = Order
        fields = ['order_status','payment_status','user','invoice_number','mobile','cart']