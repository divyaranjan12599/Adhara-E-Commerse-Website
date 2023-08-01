import json
from os import name

from django.views.generic.detail import DetailView

from core import choices
from core.admin import GalleryImageAdmin
from core.models import (Configuration, ContactUs, GalleryImage,
                         HomepageSlider, NewsletterSubscriber, Pincode, Promotion, StaticPage,CityState)
from core.utils import build_breadcrumb, build_html_head
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from shop.models import Attribute, Cart, CartProducts, Category, DiscountCategory, DiscountCoupon, HomepageCategory, Manufacturer, Order, OrderShipment, OrderShipmentAttributes, Product, ProductAttributes, ProductOption, ProductOptionAttributes, TaxClass, TaxClassBracket,ProductOptionImage, Wishlist
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView,ListView,CreateView, UpdateView,DeleteView
from django.urls.base import reverse, reverse_lazy
from shop_admin.filters import AttributeFilter, CartFilter, CartProductFilter, CategoryFilter, CityStateFilter, ConfigurationFilter, ContactUsFilter, DiscountCategoryFilter, DiscountCouponFilter, \
                GalleryImageFilter, HomepageCategoryFilter, HomepagesliderFilter, ManuFacturerFilter, NewsletterSubscriberFilter, OrderFilter, PincodeFilter, ProductFilter, PromotionFilter, \
                StaticPageFilter, TaxClassFilter, WishlistFilter
from shop_admin.forms import AttributeForm, CSVForm, CategoryForm, CityStateForm, ConfigurationForm, DiscountCouponForm, GalleryImageForm, HomepagesliderForm,\
                            NewsletterSubscriberForm, OrderShipmentFormOrder, PinCodeForm, ProductAttributeFormProduct, ProductForm, ProductOptionAttributesFormProductOption, \
                            ProductOptionFormProduct, ProductOptionImageFormProductOption, PromotionForm, StaticPageForm,TaxClassForm,TaxclassBracketsForm, \
                            DiscountCategoryForm,HomepageCategoryForm,ManuFacturerForm,DiscountCouponForm,OrderForm,OrderShipmentAttributeFormOrder
from django.views.generic.base import ContextMixin,View
from django.forms.models import inlineformset_factory
import csv
from django.core.files.temp import NamedTemporaryFile
import requests
from django.core.files import File
from django.contrib.auth.decorators import login_required
from .tasks import upload_product_data_via_csv
@user_passes_test(lambda u: u.is_superuser)
def homepage(request):
    ctx={}
    title = "ADMIN::{}".format(Configuration.get('HOME_PAGE_TITLE'))
    description = title
    ctx['html_head']=build_html_head(title=title, description=description)
    ctx['active_tab']="dashboard"
    return render(request, 'shop_admin/home.html',ctx)

class BaseView(ContextMixin):
    title = ""
    active_tab=""
    active_link=""
    description=title
    filter_query=None
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_head']=build_html_head(title=self.title,description=self.title)
        context['active_tab']=self.active_tab
        context['active_link']=self.active_link
        if self.filter_query:
            context['filter_form']=self.filter_query.form  
        return context
    
class BaseListView(ListView,BaseView):
    filterset_class=None
    paginate_by = 25
    paginate_orphans = 5
    def get_queryset(self):
        qs=super().get_queryset()
        if self.filterset_class:
            self.filter_query=self.filterset_class(self.request.GET,queryset=qs)
            return self.filter_query.qs
        return qs
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class CityStateList(BaseListView):
    template_name='shop_admin/city-state.html'
    model = CityState
    title="CityStatelist"
    active_tab="core"
    active_link="citystate"
    filterset_class=CityStateFilter         
        
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class AddCityState(CreateView,BaseView):
    template_name='shop_admin/add-city-state.html'
    model=CityState
    form_class=CityStateForm
    success_url=reverse_lazy('shopadmin:citystatelist')
    title="AddCityState"
    active_tab="core"
    active_link="citystate"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class EditCityState(UpdateView,BaseView):
    template_name='shop_admin/add-city-state.html'
    model = CityState
    form_class=CityStateForm
    success_url=reverse_lazy('shopadmin:citystatelist')
    title="EditCityState"
    active_tab="core"
    active_link="citystate"

@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class DeleteView(DeleteView,BaseView):
    template_name='shop_admin/confirm_delete.html'
    title="Delete"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch') 
class PinCodelistView(BaseListView):
    template_name = 'shop_admin/pincode.html'
    model=Pincode
    title="Pincodelist"
    active_tab="core"
    active_link="pincode"
    filterset_class=PincodeFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class AddPinCode(CreateView,BaseView):
    template_name='shop_admin/add-pincode.html'
    model=Pincode
    form_class=PinCodeForm
    success_url=reverse_lazy('shopadmin:pincodelist')
    title="AddPincode"
    active_tab="core"
    active_link="pincode"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class EditPinCode(UpdateView,BaseView):
    template_name='shop_admin/add-pincode.html'
    model = Pincode
    form_class=PinCodeForm
    success_url=reverse_lazy('shopadmin:pincodelist')
    title="EditPincode"
    active_tab="core"
    active_link="pincode"

@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class GalleryImagelistView(BaseListView):
    template_name = 'shop_admin/gallery-image.html'
    model = GalleryImage
    title="galleryimagelist"
    active_tab="core"
    active_link="galleryimage"
    filterset_class=GalleryImageFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class AddGalleryImage(CreateView,BaseView):
    template_name='shop_admin/add-gallery-image.html'
    model=GalleryImage
    form_class=GalleryImageForm
    success_url=reverse_lazy('shopadmin:galleryimagelist')
    title="Addgalleryimage"
    active_tab="core"
    active_link="galleryimage"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class EditGalleryImage(UpdateView,BaseView):
    template_name='shop_admin/add-gallery-image.html'
    model = GalleryImage
    form_class=GalleryImageForm
    success_url=reverse_lazy('shopadmin:galleryimagelist')
    title="Editgalleryimage"
    active_tab="core"
    active_link="galleryimage"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch') 
class ContactUslistView(BaseListView):
    template_name = 'shop_admin/contact-us.html'
    model = ContactUs
    title="ContactUslist"
    active_tab="core"
    active_link="contactus"
    filterset_class=ContactUsFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch') 
class ContactUsDetailView(DetailView,BaseView):
    template_name='shop_admin/contactus-detail.html'
    model=ContactUs
    title="ContactUsDetail"
    active_tab="core"
    active_link="contactus"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch') 
class ConfigurationlistView(BaseListView):
    template_name = 'shop_admin/configuration.html'
    model = Configuration
    title="Configurationlist"
    active_tab="core"
    active_link="configuration"
    filterset_class=ConfigurationFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class EditConfigurationView(UpdateView,BaseView):
    template_name='shop_admin/configuration-edit.html'
    model = Configuration
    form_class=ConfigurationForm
    success_url=reverse_lazy('shopadmin:configurationlist')
    title="EditConfiguration"
    active_tab="core"
    active_link="configuration"

@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class HomepageSliderlistView(BaseListView):
    template_name='shop_admin/homepageslider.html'
    model = HomepageSlider
    title = "HomepageSlider"
    active_tab = "core"
    active_link = "homepageslider"
    filterset_class = HomepagesliderFilter
  
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')  
class AddHomepageSlider(CreateView,BaseView):
    template_name='shop_admin/add-homepageslider.html'
    model=HomepageSlider
    form_class=HomepagesliderForm
    success_url=reverse_lazy('shopadmin:homepagesliderlist')
    title="AddHomepageslider"
    active_tab="core"
    active_link="homepageslider"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class EditHomepageSlider(UpdateView,BaseView):
    template_name = 'shop_admin/add-homepageslider.html'
    model = HomepageSlider
    form_class=HomepagesliderForm
    success_url=reverse_lazy('shopadmin:homepagesliderlist')
    title="EditHomepageslider"
    active_tab="core"
    active_link="homepageslider"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class NewsletterSubscriberlistView(BaseListView):
    template_name='shop_admin/newsletter.html'
    model = NewsletterSubscriber
    title = "NewsletterSubscriber"
    active_tab = "core"
    active_link = "newsletter"
    filterset_class = NewsletterSubscriberFilter
  
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')  
class AddNewsletterSubscriber(CreateView,BaseView):
    template_name='shop_admin/add-newsletter.html'
    model=NewsletterSubscriber
    form_class=NewsletterSubscriberForm
    success_url=reverse_lazy('shopadmin:newsletterlist')
    title="AddNewsletterSubscriber"
    active_tab="core"
    active_link="newsletter"

@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class EditNewsletterSubscriber(UpdateView,BaseView):
    template_name = 'shop_admin/add-newsletter.html'
    model = NewsletterSubscriber
    form_class=NewsletterSubscriberForm
    success_url=reverse_lazy('shopadmin:newsletterlist')
    title="EditNewsletterSubscriber"
    active_tab="core"
    active_link="newsletter"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class PromotionlistView(BaseListView):
    template_name='shop_admin/promotion.html'
    model = Promotion
    title = "Promotion"
    active_tab = "core"
    active_link = "promotion"
    filterset_class = PromotionFilter
  
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class EditPromotion(UpdateView,BaseView):
    template_name = 'shop_admin/promotion-edit.html'
    model = Promotion
    form_class=PromotionForm
    success_url=reverse_lazy('shopadmin:promotionlist')
    title="EditPromotion"
    active_tab="core"
    active_link="promotion"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class StaticPagelistView(BaseListView):
    template_name='shop_admin/staticpage.html'
    model = StaticPage
    title = "StaticPage"
    active_tab = "core"
    active_link = "staticpage"
    filterset_class = StaticPageFilter

  
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class EditStaticPage(UpdateView,BaseView):
    template_name = 'shop_admin/staticpage-edit.html'
    model = StaticPage
    form_class=StaticPageForm
    success_url=reverse_lazy('shopadmin:staticpagelist')
    title="EditStaticpage"
    active_tab="core"
    active_link="staticpage"

@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class AttributelistView(BaseListView):
    template_name='shop_admin/attribute.html'
    model = Attribute
    title = "Attribute"
    active_tab = "shop"
    active_link = "attribute"
    filterset_class = AttributeFilter

@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class AddAttribute(CreateView,BaseView):
    template_name='shop_admin/add-attribute.html'
    model=Attribute
    form_class=AttributeForm
    success_url=reverse_lazy('shopadmin:attributelist')
    title="AddAttribute"
    active_tab="shop"
    active_link="attribute"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class EditAttribute(UpdateView,BaseView):
    template_name = 'shop_admin/add-attribute.html'
    model = Attribute
    form_class=AttributeForm
    success_url=reverse_lazy('shopadmin:attributelist')
    title="EditAttribute"
    active_tab="shop"
    active_link="attribute"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class CategorylistView(BaseListView):
    template_name='shop_admin/category.html'
    model = Category
    title = "Category"
    active_tab = "shop"
    active_link = "category"
    filterset_class = CategoryFilter
 
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')      
class AddCategory(CreateView,BaseView):
    template_name = 'shop_admin/add-category.html'
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('shopadmin:categorylist')
    title = "AddCategory"
    active_tab = "shop"
    active_link = "category"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class EditCategory(UpdateView,BaseView):
    template_name = 'shop_admin/add-category.html'
    model = Category
    form_class=CategoryForm
    success_url=reverse_lazy('shopadmin:categorylist')
    title="EditCategory"
    active_tab="shop"
    active_link="category"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class ProductlistView(BaseListView):
    template_name='shop_admin/product-listing.html'
    model = Product
    title = "Product"
    active_tab = "shop"
    active_link = "product"
    filterset_class=ProductFilter
    
    def get_context_data(self, **kwargs):
        ctx = super(ProductlistView,self).get_context_data(**kwargs)
        ctx['file_form']=CSVForm()
        return ctx
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name="dispatch")
class TaxClasslistView(BaseListView):
    template_name = "shop_admin/tax-class-list.html"
    model = TaxClass
    title = "TaxClass"
    active_tab = "shop"
    active_link = "tax-class"
    filterset_class = TaxClassFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')      
class AddTaxClass(CreateView,BaseView):
    template_name = 'shop_admin/add-taxclass.html'
    model = TaxClass
    form_class = TaxClassForm
    title = "AddTaxClass"
    active_tab = "shop"
    active_link = "tax-class"
    
    def get_formset(self):
        return inlineformset_factory(TaxClass,TaxClassBracket,form=TaxclassBracketsForm,extra=1,can_delete=True)

    def get_context_data(self, **kwargs):
        context= super(AddTaxClass,self).get_context_data(**kwargs)
        TaxClassBracketInlineFormset=self.get_formset()
        context['taxclass_bracket_formset']=TaxClassBracketInlineFormset()
        return context
    
    def post(self,request,*args,**kwargs):
        self.object=None
        form_class = self.get_form_class()
        form=self.get_form(form_class)
        TaxClassBracketInlineFormset=self.get_formset()
        taxclass_bracket_formset=TaxClassBracketInlineFormset(self.request.POST)
        if form.is_valid() and taxclass_bracket_formset.is_valid():
            return self.form_valid(form,taxclass_bracket_formset)
        else:
            return self.form_invalid(form,taxclass_bracket_formset)
        
    def form_valid(self, form,taxclass_bracket_formset):
        self.object = form.save(commit=False)
        self.object.save()
        taxclassbrackets = taxclass_bracket_formset.save(commit=False)
        for taxclassbracket in taxclassbrackets:
            taxclassbracket.tax_class = self.object
            taxclassbracket.save()
        return redirect(reverse('shopadmin:taxclasslist'))
    
    def form_invalid(self, form,taxclass_bracket_formset):
        return self.render_to_response(self.get_context_data(form=form,taxclass_bracket_formset=taxclass_bracket_formset))
    
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')      
class EditTaxClass(UpdateView,BaseView):
    template_name = 'shop_admin/edit-taxclass.html'
    model = TaxClass
    form_class = TaxClassForm
    success_url = reverse_lazy("shopadmin:taxclasslist")
    active_tab="shop"
    active_link="taxclass"
    
    def get_formset(self):
        return inlineformset_factory(TaxClass,TaxClassBracket,form=TaxclassBracketsForm,extra=1,can_delete=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        TaxClassBracketInlineFormset = self.get_formset()
        formset = TaxClassBracketInlineFormset(instance=self.get_object())
        context['taxclass_bracket_formset']=formset
        return context    
    
    def post(self,request,*args,**kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        TaxClassBracketInlineFormset = self.get_formset()
        taxclass_bracket_formset = TaxClassBracketInlineFormset(self.request.POST,instance=self.get_object())
        
        if form.is_valid() and taxclass_bracket_formset.is_valid():
            return self.form_valid(form,taxclass_bracket_formset)
        else:
            return self.form_invalid(form,taxclass_bracket_formset)
        
    def form_valid(self, form,taxclass_bracket_formset):
        self.object = form.save(commit=False)
        self.object.save()
        taxclassbrackets = taxclass_bracket_formset.save(commit=False)
        for taxclassbracket in taxclassbrackets:
            taxclassbracket.tax_class = self.object
            taxclassbracket.save()
        return redirect(reverse('shopadmin:taxclasslist'))
    
    def form_invalid(self, form,taxclass_bracket_formset):
        return self.render_to_response(self.get_context_data(form=form,taxclass_bracket_formset=taxclass_bracket_formset))
            
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch') 
class product_data_file_uploading(View):
    def post(self,request,*args,**kwrags):
        form=CSVForm(request.POST,request.FILES)
        if form.is_valid():
            paramFile=form.cleaned_data['csv_file']
            category_choice=form.cleaned_data['category_choice']
            decode_file=paramFile.read().decode('utf-8').splitlines()
            data = csv.DictReader(decode_file)
            for i,row in enumerate(data):
                if i != 0:
                    row=dict(row)
                    #product uploading using task queue celery
                    upload_product_data_via_csv.delay(row,category_choice)
            return redirect(reverse("shopadmin:productlist")) 
        return redirect(reverse("shopadmin:productlist")) 
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')      
class AddProduct(CreateView,BaseView):
    template_name = 'shop_admin/add-product.html'
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('shopadmin:productlist')
    title = "AddProduct"
    active_tab = "shop"
    active_link = "product"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class EditProduct(UpdateView,BaseView):
    template_name = 'shop_admin/add-product.html'
    model = Product
    form_class=ProductForm
    success_url=reverse_lazy('shopadmin:productlist')
    title="EditProduct"
    active_tab="shop"
    active_link="product"
    
    

@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class AddProductOptionProduct(CreateView,BaseView):
    template_name='shop_admin/add-productOptionusingproduct.html'
    model=ProductOption
    form_class=ProductOptionFormProduct
    title="AddProductOption"
    active_tab="shop"
    active_link="product"

    
    def get_context_data(self, **kwargs):
        ctx= super().get_context_data(**kwargs)
        ctx['product']=Product.objects.get(id=self.kwargs.get('product_id'))
        return ctx
    
    def form_valid(self,form):
        form.instance.product=Product.objects.get(id=self.kwargs.get('product_id'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.product.edit_url

@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class EditProductOptionProduct(UpdateView,BaseView):
    template_name = 'shop_admin/add-productOptionusingproduct.html'
    model = ProductOption
    form_class=ProductOptionFormProduct
    success_url=reverse_lazy('shopadmin:productlist')
    title="EditProductOption"
    active_tab="shop"
    active_link="product"
    
    def get_success_url(self):
        object = self.get_object()
        return object.product.edit_url
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class AddProductAttributeProduct(CreateView,BaseView):
    template_name='shop_admin/add-productattributeusingproduct.html'
    model=ProductAttributes
    form_class=ProductAttributeFormProduct
    title="AddProductAttribute"
    active_tab="shop"
    active_link="product"
    
    def get_context_data(self, **kwargs):
        ctx= super().get_context_data(**kwargs)
        ctx['product']=Product.objects.get(id=self.kwargs.get('product_id'))
        return ctx
    
    def form_valid(self,form):
        form.instance.product=Product.objects.get(id=self.kwargs.get('product_id'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.product.edit_url
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class EditProductAttributeProduct(UpdateView,BaseView):
    template_name = 'shop_admin/add-productattributeusingproduct.html'
    model = ProductAttributes
    form_class=ProductAttributeFormProduct
    title="EditProductAttribute"
    active_tab="shop"
    active_link="product"
    
    def get_success_url(self):
        object = self.get_object()
        return object.product.edit_url
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class AddProductOptionAttributeProductOption(CreateView,BaseView):
    template_name='shop_admin/add-productOptionAttributeProductOption.html'
    model=ProductOptionAttributes
    form_class=ProductOptionAttributesFormProductOption
    title="AddProductOptionAttribute"
    active_tab="shop"
    active_link="product"
    
    def get_context_data(self, **kwargs):
        ctx= super().get_context_data(**kwargs)
        ctx['product_option']=ProductOption.objects.get(id=self.kwargs.get('productoption_id'))
        return ctx
    
    def form_valid(self,form):
        form.instance.product_option=ProductOption.objects.get(id=self.kwargs.get('productoption_id'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.product_option.edit_url 
    
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class EditProductOptionAttributeProductOption(UpdateView,BaseView):
    template_name = 'shop_admin/add-productOptionAttributeProductOption.html'
    model = ProductOptionAttributes
    form_class=ProductOptionAttributesFormProductOption
    title="EditProductOptionAttribute"
    active_tab="shop"
    active_link="product"
    
    def get_success_url(self):
        object = self.get_object()
        return object.product_option.edit_url
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class AddProductOptionImageProductOption(CreateView,BaseView):
    template_name='shop_admin/add-productOptionImageProductOption.html'
    model=ProductOptionImage
    form_class=ProductOptionImageFormProductOption
    title="AddProductOptionImage"
    active_tab="shop"
    active_link="product"
    
    def get_context_data(self, **kwargs):
        ctx= super().get_context_data(**kwargs)
        ctx['product_option']=ProductOption.objects.get(id=self.kwargs.get('productoption_id'))
        return ctx
    
    def form_valid(self,form):
        form.instance.product_option=ProductOption.objects.get(id=self.kwargs.get('productoption_id'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.product_option.edit_url 
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class EditProductOptionImageProductOption(UpdateView,BaseView):
    template_name = 'shop_admin/add-productOptionImageProductOption.html'
    model = ProductOptionImage
    form_class=ProductOptionImageFormProductOption
    title="EditProductOptionImage"
    active_tab="shop"
    active_link="product"
    
    def get_success_url(self):
        object = self.get_object()
        return object.product_option.edit_url
    
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class DiscountCategorylistView(BaseListView):
    template_name='shop_admin/discount-categories.html'
    model = DiscountCategory
    title = "DiscountCategories"
    active_tab = "shop"
    active_link = "discount_categories"
    filterset_class = DiscountCategoryFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class AddDiscountCategory(CreateView,BaseView):
    template_name = 'shop_admin/add-discountcategory.html'
    model = DiscountCategory
    form_class=DiscountCategoryForm
    success_url=reverse_lazy('shopadmin:discountcategorylist')
    title="AddDiscountCategory"
    active_tab="shop"
    active_link="discount_categories"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class EditDiscountCategory(UpdateView,BaseView):
    template_name = 'shop_admin/add-discountcategory.html'
    model = DiscountCategory
    form_class=DiscountCategoryForm
    title="EditDiscountCategory"
    active_tab="shop"
    active_link="discount_categories"
    success_url=reverse_lazy('shopadmin:discountcategorylist')
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class HomepageCategorylistView(BaseListView):
    template_name='shop_admin/homepage-category.html'
    model = HomepageCategory
    title = "HomepageCategory"
    active_tab = "shop"
    active_link = "homepage_category"
    filterset_class = HomepageCategoryFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class AddHomepageCategory(CreateView,BaseView):
    template_name = 'shop_admin/add-homepagecategory.html'
    model = HomepageCategory
    form_class=HomepageCategoryForm
    success_url=reverse_lazy('shopadmin:homepagecategorylist')
    title="AddHomepageCategory"
    active_tab="shop"
    active_link="homepage_category"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class EditHomepageCategory(UpdateView,BaseView):
    template_name = 'shop_admin/add-homepagecategory.html'
    model = HomepageCategory
    form_class=HomepageCategoryForm
    title="EditHomepageCategory"
    active_tab="shop"
    active_link="homepage_category"
    success_url=reverse_lazy('shopadmin:homepagecategorylist')
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class ManufacturerlistView(BaseListView):
    template_name='shop_admin/manufacturer.html'
    model = Manufacturer
    title = "Manufacturer"
    active_tab = "shop"
    active_link = "manufacturer"
    filterset_class = ManuFacturerFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class AddManufacturer(CreateView,BaseView):
    template_name = 'shop_admin/add-manufacturer.html'
    model = Manufacturer
    form_class=ManuFacturerForm
    success_url=reverse_lazy('shopadmin:manufacturerlist')
    title="AddManufacturer"
    active_tab="shop"
    active_link="manufacturer"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class EditManufacturer(UpdateView,BaseView):
    template_name = 'shop_admin/add-manufacturer.html'
    model = Manufacturer
    form_class=ManuFacturerForm
    title="EditManuFacturer"
    active_tab="shop"
    active_link="manufacturer"
    success_url=reverse_lazy('shopadmin:manufacturerlist')
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class DiscountCouponlistView(BaseListView):
    template_name='shop_admin/discountcoupon.html'
    model = DiscountCoupon
    title = "DiscountCoupon"
    active_tab = "shop"
    active_link = "discountcoupon"
    filterset_class = DiscountCouponFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')    
class AddDiscountCoupon(CreateView,BaseView):
    template_name = 'shop_admin/add-discountcoupon.html'
    model = DiscountCoupon
    form_class =DiscountCouponForm
    success_url=reverse_lazy('shopadmin:discountcouponlist')
    title="AddDiscountCoupon"
    active_tab="shop"
    active_link="discountcoupon"
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class EditDiscountCoupon(UpdateView,BaseView):
    template_name = 'shop_admin/add-discountcoupon.html'
    model = DiscountCoupon
    form_class = DiscountCouponForm
    title="EditDiscountCoupon"
    active_tab="shop"
    active_link="discountcoupon"
    success_url=reverse_lazy('shopadmin:discountcouponlist')    
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class CartslistView(BaseListView):
    template_name='shop_admin/carts.html'
    model = Cart
    title = "Cart"
    active_tab = "shop"
    active_link = "cart"
    filterset_class = CartFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class CartDetailView(DetailView,BaseView):
    template_name = 'shop_admin/cartdetail.html'
    model = Cart
    title="CartDetail"
    active_tab="shop"
    active_link="cart"

@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class WishlistsView(BaseListView):
    template_name='shop_admin/wishlists.html'
    model = Wishlist
    title = "Wishlist"
    active_tab = "shop"
    active_link = "wishlist"
    filterset_class = WishlistFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class CartProductslistView(BaseListView):
    template_name='shop_admin/cartproduct.html'
    model = CartProducts
    title = "CartProducts"
    active_tab = "shop"
    active_link = "cartproduct"
    filterset_class = CartProductFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class CartProductDetailView(DetailView,BaseView):
    template_name = 'shop_admin/cartproductdetail.html'
    model = CartProducts
    title="CartProductDetail"
    active_tab="shop"
    active_link="cartproduct"
    
class OrderlistView(BaseListView):
    template_name='shop_admin/order.html'
    model = Order
    title = "Order"
    active_tab = "shop"
    active_link = "order"
    filterset_class = OrderFilter
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class EditOrder(UpdateView,BaseView):
    template_name = 'shop_admin/edit-order.html'
    model = Order
    form_class=OrderForm
    title="EditOrder"
    active_tab="shop"
    active_link="order"
    success_url=reverse_lazy('shopadmin:orderlist')
    
    def get_context_data(self, **kwargs):
        ctx= super().get_context_data(**kwargs)
        ctx['order_status']=[choices.OrderStatus.SHIPPED,choices.OrderStatus.COMPLETE,choices.OrderStatus.CANCELED]
        return ctx
 
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')      
class AddOrderShipmentOrder(CreateView,BaseView):
    template_name = 'shop_admin/add-ordershipmentorder.html'
    model = OrderShipment
    form_class=OrderShipmentFormOrder
    title="AddOrderShipment"
    active_tab="shop"
    active_link="order"

    def get_context_data(self, **kwargs):
        ctx= super().get_context_data(**kwargs)
        ctx['order']=Order.objects.get(id=self.kwargs.get('order_id'))
        return ctx
    
    def form_valid(self,form):
        form.instance.order=Order.objects.get(id=self.kwargs.get('order_id'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.order.edit_url 

@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class EditOrderShipmentOrder(UpdateView,BaseView):
    template_name = 'shop_admin/add-ordershipmentorder.html'
    model = OrderShipment
    form_class=OrderShipmentFormOrder
    title="AddOrderShipment"
    active_tab="shop"
    active_link="order"
    
    def get_success_url(self):
        object = self.get_object()
        return object.order.edit_url
   
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')
class AddOrderShipmentAttributeOrder(CreateView,BaseView):
    template_name='shop_admin/add-ordershipmentattributeorder.html'
    model=OrderShipmentAttributes
    form_class=OrderShipmentAttributeFormOrder
    title="AddOrderShipment"
    active_tab="shop"
    active_link="order"
    
    def get_context_data(self, **kwargs):
        ctx= super().get_context_data(**kwargs)
        ctx['order']=Order.objects.get(id=self.kwargs.get('order_id'))
        return ctx
    
    def form_valid(self,form):
        form.instance.order=Order.objects.get(id=self.kwargs.get('order_id'))
        return super(AddOrderShipmentAttributeOrder,self).form_valid(form)
    
    def get_success_url(self):
        return self.object.order.edit_url 
    
@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')   
class EditOrderShipmentAttributeOrder(UpdateView,BaseView):
    template_name = 'shop_admin/add-ordershipmentattributeorder.html'
    model = OrderShipmentAttributes
    form_class=OrderShipmentAttributeFormOrder
    title="EditOrderShipmentAttribute"
    active_tab="shop"
    active_link="order"
    
    def get_success_url(self):
        object = self.get_object()
        return object.order.edit_url
    
class OrderShipmentView(TemplateView):
    template_name = 'storefront/shop/admin/shipment_orders.html'
    
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def breadcrumb(self):

        l = [{
            'title': "My Account",
            'text': "My Account",
            'url': reverse('users:account')
        }, {
            'title': 'Shipment Ready Orders',
            'text': 'Shipment Ready Orders',
            'url': ''
        }]

        return build_breadcrumb(l)

    def html_head(self):
        s='Shipments'
        return build_html_head(title=s, description=s)

    def get_context(self, request, *args, **kwargs):
        ctx={}
        ctx['breadcrumb'] = self.breadcrumb()
        ctx['html_head'] = self.html_head()
        ctx['orders'] = Order.shipment_ready_orders()
        return ctx

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return render(request, self.template_name, self.get_context(request, *args, **kwargs))

@method_decorator(user_passes_test(lambda u: u.is_superuser),name='dispatch')       
class OrderShipmentViewShopadmin(BaseListView):
    template_name = 'shop_admin/shipment_orders.html'
    model = Order
    title = "Order"
    active_tab = "shop"
    active_link = "shipmentorder"
      
    def get_queryset(self):
        return Order.shipment_ready_orders()

