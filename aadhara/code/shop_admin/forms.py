from django import forms
from django.db.models import fields
from django.forms import widgets
from django.forms.models import inlineformset_factory
from core.models import CityState, GalleryImage, HomepageSlider, NewsletterSubscriber, Pincode,Configuration,Promotion, StaticPage
from shop.admin import AttributeAdmin
from shop.models import Attribute, Category, DiscountCoupon, HomepageCategory, Manufacturer, Order, OrderShipment, OrderShipmentAttributes, Product, ProductAttributes, ProductOption, ProductOptionAttributes,TaxClass, TaxClassBracket,ProductOptionImage \
                        ,DiscountCategory

class BaseModelForm(forms.ModelForm):
    def __init__(self,*args,**kwrgs):
        super(BaseModelForm,self).__init__(*args,**kwrgs)
        for field_name,field in self.fields.items():
            self.add_class_attributes(field)
    
    def add_class_attributes(self,field):
        if field.widget.input_type == 'file':
            self.add_form_control_file_class(field)
        elif field.widget.input_type == 'checkbox':
            self.add_form_check_input_class(field)
        else:
            self.add_form_control_class(field)
    
    def add_form_control_class(self,field):
        if field.widget.attrs.get('class'):
            field.widget.attrs['class'] += ' form-control '
        else:
            field.widget.attrs['class'] = ' form-control '
    
    def add_form_control_file_class(self,field):
        if field.widget.attrs.get('class'):
            field.widget.attrs['class'] += ' form-control-file '
        else:
            field.widget.attrs['class'] = ' form-control-file '
            
    def add_form_check_input_class(self,field):
        if field.widget.attrs.get('class'):
            field.widget.attrs['class'] += ' form-check-input '
        else:
            field.widget.attrs['class'] = ' form-check-input '

    
class CityStateForm(BaseModelForm):
    class Meta:
        model = CityState
        fields = ['object_status','name','parent','type']
        
class PinCodeForm(BaseModelForm):
    class Meta:
        model = Pincode
        fields=['pincode','city_state']
        
class GalleryImageForm(BaseModelForm):
    class Meta:
        model = GalleryImage
        fields = ['title','image','priority']

class ConfigurationForm(BaseModelForm):
    class Meta:
        model = Configuration
        fields=['key','value','editable']
        widgets={'key':forms.TextInput(attrs={"readonly":True})}
        
class HomepagesliderForm(BaseModelForm):
    class Meta:
        model = HomepageSlider
        fields = ['name','enabled','url','title','subtitle','button_text','priority','image']
        
class NewsletterSubscriberForm(BaseModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields=['object_status','email']
        
class PromotionForm(BaseModelForm):
    class Meta:
        model = Promotion
        fields = ['name','enabled','url','message']
        widgets={'name':forms.TextInput(attrs={"readonly":True})}
        
class StaticPageForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'id':"ckeditor", 'cols':"30" ,'rows':"15" ,'class':"ckeditor"}))
    class Meta:
        model = StaticPage
        fields = ['title','meta_description','content','slug']
        widgets = {'title':forms.TextInput(attrs={'class':'form-control'}),
                   'meta_description':forms.TextInput(attrs={'class':'form-control'}),
                   'slug':forms.TextInput(attrs={'class':'form-control','readonly':True})}
        
class AttributeForm(BaseModelForm):
    class Meta:
        model=Attribute
        fields = ['name']
        
class CategoryForm(forms.ModelForm):
    size_chart = forms.CharField(required=False,widget=forms.Textarea(attrs={'id':"ckeditor", 'cols':"30" ,'rows':"15" ,'class':"ckeditor"}))
    shipping_and_returns = forms.CharField(required=False,widget=forms.Textarea(attrs={'id':"ckeditor", 'cols':"30" ,'rows':"15" ,'class':"ckeditor"}))
    class Meta:
        model = Category
        fields = ['name','parent','priority','size_chart','shipping_and_returns','placeholder']
        widgets = {'name':forms.TextInput(attrs={'class':'form-control'}),
                   'parent':forms.Select(attrs={'class':'form-control'}),
                   'priority':forms.TextInput(attrs={'class':'form-control'}),
                   'placeholder':forms.Textarea(attrs={'class':'form-control',"id":"placeTextarea" ,"rows":"3"})}
        
class TaxClassForm(forms.ModelForm):
    class Meta:
        model = TaxClass
        fields = ['name','description']
        widgets = {'name':forms.TextInput(attrs={'class':'form-control'}),'description':forms.Textarea(attrs={'class':'form-control',"id":"placeTextarea" ,"rows":"3"})}
        
        
class TaxclassBracketsForm(BaseModelForm):
    class Meta:
        model = TaxClassBracket
        fields = ['min_rate','max_rate','cgst_rate','sgst_rate','igst_rate']
        
        
class ProductForm(forms.ModelForm):
    description = forms.CharField(required=False,widget=forms.Textarea(attrs={'id':"ckeditor", 'cols':"30" ,'rows':"15" ,'class':"ckeditor"}))
    class Meta:
        model = Product
        fields = ['name','summary','manufacturer','primary_category','categories','description','hsn','sku','location','status','return_days','youtube_link','weight_gram','tax_class','primary_attribute','width','height','length']
        widgets = {'name':forms.TextInput(attrs={'class':'form-control'}),
                   'summary':forms.TextInput(attrs={'class':'form-control'}),
                   'manufacturer':forms.Select(attrs={'class':'form-control'}),
                   'primary_category':forms.Select(attrs={'class':'form-control'}),
                   'categories':forms.SelectMultiple(attrs={'class':'form-control'}),
                   'hsn':forms.TextInput(attrs={'class':'form-control'}),
                   'sku':forms.TextInput(attrs={'class':'form-control'}),
                   'location':forms.Select(attrs={'class':'form-control'}),
                   'status':forms.Select(attrs={'class':'form-control'}),
                   'return_days':forms.NumberInput(attrs={'class':'form-control'}),
                   'tax_class':forms.Select(attrs={'class':'form-control'}),
                   'youtube_link':forms.URLInput(attrs={'class':'form-control'}),
                   'weight_gram':forms.NumberInput(attrs={'class':'form-control'}),
                   'primary_attribute':forms.Select(attrs={'class':'form-control'}),
                   'width':forms.TextInput(attrs={'class':'form-control'}),
                   'height':forms.TextInput(attrs={'class':'form-control'}),
                   'length':forms.TextInput(attrs={'class':'form-control'}),}
  
def get_choice_category():
    NULL_CHOICE=[]
    return NULL_CHOICE+[(choice.pk,choice) for choice in Category.objects.all()]
        
class CSVForm(forms.Form):
    csv_file = forms.FileField(widget=forms.FileInput(attrs={'class':'form-control-file','required':True}))
    category_choice = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control','required':True}),choices=get_choice_category)
    
class ProductOptionFormProduct(BaseModelForm):
    class Meta:
        model = ProductOption
        fields = ['product','sku','quantity','priority','list_price','selling_price']
        widgets = {'product':forms.HiddenInput()}
        
class ProductAttributeFormProduct(BaseModelForm):
    class Meta:
        model = ProductAttributes
        fields =['product','name','value']
        widgets={'product':forms.HiddenInput()}


class ProductOptionAttributesFormProductOption(BaseModelForm):
    class Meta:
        model = ProductOptionAttributes
        fields = ['product_option','attribute','value','label','priority']
        widgets ={'product_option':forms.HiddenInput()}
        
class ProductOptionImageFormProductOption(BaseModelForm):
    class Meta:
        model = ProductOptionImage
        fields = ['product_option','image','is_common','priority']
        widgets = {'product_option':forms.HiddenInput()}
        
class DiscountCategoryForm(BaseModelForm):
    class Meta:
        model = DiscountCategory
        fields = ['name','category_type','min_cart_amount','type','value','start_date_time','end_date_time']
        widgets = {'start_date_time':forms.DateTimeInput(format="%m/%d/%Y %H:%M:%S",attrs={'placeholder':'12/23/2021 14:34:3'}),
                   'end_date_time':forms.DateTimeInput(format="%m/%d/%Y %H:%M:%S",attrs={'placeholder':'12/23/2021 14:34:3'})
                   }
class HomepageCategoryForm(BaseModelForm):
    class Meta:
        model = HomepageCategory
        fields = ['category','enabled','title','subtitle','button_text','priority','image']
        
class ManuFacturerForm(BaseModelForm):
    class Meta:
        model = Manufacturer
        fields = ['name']
        
class DiscountCouponForm(BaseModelForm):
    class Meta:
        model = DiscountCoupon
        fields = ['code','name','start_date','end_date','discount_value','discount_type','max_discount','min_cart_amount','summary','discount_image','coupon_type']
        widgets = {'start_date':forms.DateInput(format="%m/%d/%Y",attrs={'placeholder':'12/23/2021'}),
                   'end_date':forms.DateInput(format="%m/%d/%Y",attrs={'placeholder':'12/24/2021'})}
        
class OrderForm(BaseModelForm):
    class Meta:
        model = Order
        fields = ['name','email','mobile','shipping_address','order_status']

class OrderShipmentFormOrder(BaseModelForm):
    class Meta:
        model = OrderShipment
        fields = ['order','shipment_company','shipped_on','tracking_no']
        widgets = {'order':forms.HiddenInput()}
        
class OrderShipmentAttributeFormOrder(BaseModelForm):
    class Meta:
        model = OrderShipmentAttributes
        fields = ['order','key','value']
        widgets ={'order':forms.HiddenInput()}