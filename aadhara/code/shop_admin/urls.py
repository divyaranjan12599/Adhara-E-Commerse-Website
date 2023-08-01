from os import name
from django.contrib import admin
from django.urls import path
from django.urls.base import reverse_lazy
from core.models import CityState, GalleryImage, NewsletterSubscriber,Pincode,HomepageSlider, Promotion
from shop.models import Attribute, Category, DiscountCoupon, HomepageCategory, Manufacturer, OrderShipment, OrderShipmentAttributes, ProductAttributes, ProductOption, ProductOptionAttributes, ProductOptionImage, TaxClass,Product,DiscountCategory
from . import views

app_name = 'shopadmin'
urlpatterns = [
    path('', views.homepage,name='home'),
    
    path('citystatelist/',views.CityStateList.as_view(),name='citystatelist'),
    path('addcitystate/',views.AddCityState.as_view(),name='addcitystate'),
    path('updatecitystate/<int:pk>/',views.EditCityState.as_view(),name='updatecitystate'),
    path('Deleteviewcitystate/<int:pk>/',views.DeleteView.as_view(model=CityState,success_url=reverse_lazy('shopadmin:citystatelist'),active_tab="core",active_link="citystate"),name='deletecitystate'),
    
    path('Pincode/',views.PinCodelistView.as_view(),name='pincodelist'),
    path('addpincode/',views.AddPinCode.as_view(),name='addpincode'),
    path('pincode/<int:pk>/',views.EditPinCode.as_view(),name='updatepincode'),
    path('DeleteViewpincode/<int:pk>/',views.DeleteView.as_view(model=Pincode,success_url=reverse_lazy('shopadmin:pincodelist'),active_tab="core",active_link="pincode"),name='deletepincode'),
    
    path('galleryimagelist/',views.GalleryImagelistView.as_view(),name='galleryimagelist'),
    path('addgalleryimage/',views. AddGalleryImage.as_view(),name='addgalleryimage'),
    path('updategalleryimage/<int:pk>/',views.EditGalleryImage.as_view(),name="editgalleryimage"),
    path('Deleteviewgalleryimage/<int:pk>/',views.DeleteView.as_view(model=GalleryImage,success_url=reverse_lazy('shopadmin:galleryimagelist'),active_tab="core",active_link="galleryimage"),name="deletegalleryimage"),
    
    path("contactuslist/",views.ContactUslistView.as_view(),name="contactuslist"),
    path('contactusdetail/<int:pk>/',views.ContactUsDetailView.as_view(),name="contactusdetail"),
    
    path("configuration/",views.ConfigurationlistView.as_view(),name="configurationlist"),
    path("editconfiguration/<int:pk>/",views.EditConfigurationView.as_view(),name="editconfiguration"),
    
    path('homepageslider/',views.HomepageSliderlistView.as_view(),name="homepagesliderlist"),
    path('addhomepageslider/',views.AddHomepageSlider.as_view(),name="addhomepageslider"),
    path('edithomepageslider/<int:pk>/',views.EditHomepageSlider.as_view(),name='edithomepageslider'),
    path("deletehomepageslider/<int:pk>/",views.DeleteView.as_view(model=HomepageSlider,success_url=reverse_lazy('shopadmin:homepagesliderlist'),active_tab="core",active_link="homepageslider"),name="deletehomepageslider"),
    
    path('newslettersubscriber/',views.NewsletterSubscriberlistView.as_view(),name="newsletterlist"),
    path('addnewslettersubscriber/',views.AddNewsletterSubscriber.as_view(),name="addnewsletter"),
    path('editnewslettersubscriber/<int:pk>/',views.EditNewsletterSubscriber.as_view(),name="editnewsletter"),
    path('deletenewsletter/<int:pk>/',views.DeleteView.as_view(model=NewsletterSubscriber,success_url=reverse_lazy('shopadmin:newsletterlist'),active_tab="core",active_link="newsletter"),name="deletenewsletter"),
    
    path('promotion/',views.PromotionlistView.as_view(),name="promotionlist"),
    path('editpromotion/<int:pk>/',views.EditPromotion.as_view(),name='editpromotion'),
    
    path('staticpage/',views.StaticPagelistView.as_view(),name="staticpagelist"),
    path('editstaticpage/<int:pk>/',views.EditStaticPage.as_view(),name='editstaticpage'),

    path('attribute/',views.AttributelistView.as_view(),name="attributelist"),
    path('addattribute/',views.AddAttribute.as_view(),name="addattribute"),
    path("editattribute/<int:pk>/",views.EditAttribute.as_view(),name="editattribute"),
    path("deleteattribute/<int:pk>/",views.DeleteView.as_view(model=Attribute,success_url=reverse_lazy('shopadmin:attributelist'),active_tab="shop",active_link="attribute"),name='deleteattribute'),
    
    path('category/',views.CategorylistView.as_view(),name="categorylist"),
    path('addcategory/',views.AddCategory.as_view(),name="addcategory"),
    path("editcategory/<int:pk>/",views.EditCategory.as_view(),name="editcategory"),
    path("deletecategory/<int:pk>/",views.DeleteView.as_view(model=Category,success_url=reverse_lazy('shopadmin:categorylist'),active_tab="shop",active_link="category"),name='deletecategory'),
    
    path("product/",views.ProductlistView.as_view(),name="productlist"),
    path("addproduct/",views.AddProduct.as_view(),name="addproduct"),
    path("editproduct/<int:pk>/",views.EditProduct.as_view(),name="editproduct"),
    path("deleteproduct/<int:pk>/",views.DeleteView.as_view(model=Product,success_url=reverse_lazy('shopadmin:productlist'),active_tab="shop",active_link="product"),name="deleteproduct"),
    path("fileupload",views.product_data_file_uploading.as_view(),name="fileupload"),
        
    path("addproductOptionuproduct/<int:product_id>/",views.AddProductOptionProduct.as_view(),name="addproductoptionproduct"),
    path("editproductOptionproduct/<int:pk>/",views.EditProductOptionProduct.as_view(),name="editproductoptionproduct"),
    path("deleteproductOptionproduct/<int:pk>/",views.DeleteView.as_view(model=ProductOption,success_url=reverse_lazy('shopadmin:productlist'),active_tab="shop",active_link="product"),name="deleteproductoptionproduct"),
    
    path("addproductattributeproduct/<int:product_id>/",views.AddProductAttributeProduct.as_view(),name="addproductattributeproduct"),
    path("editproductattributeproduct/<int:pk>/",views.EditProductAttributeProduct.as_view(),name="editproductattributeproduct"),
    path("deleteproductattributeproduct/<int:pk>/",views.DeleteView.as_view(model=ProductAttributes,success_url=reverse_lazy('shopadmin:productlist'),active_tab="shop",active_link="product"),name="deleteproductattributeproduct"),
    
    
    path("addproductoptionattributeproductoption/<int:productoption_id>/",views.AddProductOptionAttributeProductOption.as_view(),name="addproductoptionattributeproductoption"),
    path("editproductOptionattributeproductoption/<int:pk>/",views.EditProductOptionAttributeProductOption.as_view(),name="editproductoptionattributeproductoption"),
    path("deleteproductOptionattributeproductoption/<int:pk>/",views.DeleteView.as_view(model=ProductOptionAttributes,success_url=reverse_lazy('shopadmin:productlist'),active_tab="shop",active_link="product"),name="deleteproductoptionattributeproductoption"),
    
    path("addproductoptionimageproductoption/<int:productoption_id>/",views.AddProductOptionImageProductOption.as_view(),name="addproductoptionimageproductoption"),
    path("editproductOptionimageproductoption/<int:pk>/",views.EditProductOptionImageProductOption.as_view(),name="editproductoptionimageproductoption"),
    path("deleteproductOptionimageproductoption/<int:pk>/",views.DeleteView.as_view(model=ProductOptionImage,success_url=reverse_lazy('shopadmin:productlist'),active_tab="shop",active_link="product"),name="deleteproductoptionimageproductoption"),
    
    
        
    path("tax-class/",views.TaxClasslistView.as_view(),name="taxclasslist"),
    path("add-tax-class/",views.AddTaxClass.as_view(),name="addtaxclass"),
    path("edittaxclass/<int:pk>/",views.EditTaxClass.as_view(),name="edittaxclass"),
    path("deletetaxclass/<int:pk>/",views.DeleteView.as_view(model=TaxClass,success_url=reverse_lazy("shopadmin:taxclasslist"),active_tab="shop",active_link="taxclass"),name="deletetaxclass"),
    
    path("discount-category/",views.DiscountCategorylistView.as_view(),name="discountcategorylist"),
    path("add-discount-category/",views.AddDiscountCategory.as_view(),name="adddiscountcategory"),
    path('editdiscountcategory/<int:pk>/',views.EditDiscountCategory.as_view(),name='editdiscountcategory'),
    path("deletediscountcategory/<int:pk>/",views.DeleteView.as_view(model=DiscountCategory,success_url=reverse_lazy('shopadmin:discountcategorylist'),active_tab="shop",active_link="discount_categories"),name="deletediscountcategory"),
    
    path('homepagecategory/',views.HomepageCategorylistView.as_view(),name="homepagecategorylist"),
    path('addhomepagecategory/',views.AddHomepageCategory.as_view(),name='addhomepagecategory'),
    path('edithomepagecategory/<int:pk>/',views.EditHomepageCategory.as_view(),name='edithomepagecategory'),
    path("deletehomepagecategory/<int:pk>/",views.DeleteView.as_view(model=HomepageCategory,success_url=reverse_lazy('shopadmin:homepagecategorylist'),active_tab="shop",active_link="homepage_category"),name="deletehomepagecategory"),
    
    path('manufacture/',views.ManufacturerlistView.as_view(),name="manufacturerlist"),
    path('addmanufacturer/',views.AddManufacturer.as_view(),name='addmanufacturer'),
    path('editmanufacturer/<int:pk>/',views.EditManufacturer.as_view(),name='editmanufacturer'),
    path("deletemanufacturer/<int:pk>/",views.DeleteView.as_view(model=Manufacturer,success_url=reverse_lazy('shopadmin:manufacturerlist'),active_tab="shop",active_link="manufacturer"),name="deletemanufacturer"),
    
    path('discountcoupon/',views.DiscountCouponlistView.as_view(),name="discountcouponlist"),
    path('adddiscountcoupon/',views.AddDiscountCoupon.as_view(),name='adddiscountcoupon'),
    path('editdiscountcoupon/<int:pk>/',views.EditDiscountCoupon.as_view(),name='editdiscountcoupon'),
    path("deletediscountcoupon/<int:pk>/",views.DeleteView.as_view(model=DiscountCoupon,success_url=reverse_lazy('shopadmin:discountcouponlist'),active_tab="shop",active_link="discountcoupon"),name="deletediscountcoupon"),
    
    path('carts/',views.CartslistView.as_view(),name="cartlist"),
    path('cartdetail/<int:pk>/',views.CartDetailView.as_view(),name="cartdetail"),
    
    path('wishlist/',views.WishlistsView.as_view(),name="wishlist"),
    
    path('cartproducts/',views.CartProductslistView.as_view(),name="cartproductlist"),
    path('cartproductdetail/<int:pk>/',views.CartProductDetailView.as_view(),name="cartproductdetail"),

    path('orders/',views.OrderlistView.as_view(),name="orderlist"),
    path('editorder/<int:pk>/',views.EditOrder.as_view(),name="editorder"),

    path('addordershipmentorder/<int:order_id>/',views.AddOrderShipmentOrder.as_view(),name="addordershipmentorder"),
    path('editordershipment/<int:pk>/',views.EditOrderShipmentOrder.as_view(),name="editordershipmentorder"),
    path("deleteordershipment/<int:pk>/",views.DeleteView.as_view(model=OrderShipment,success_url=reverse_lazy('shopadmin:orderlist'),active_tab="shop",active_link="order"),name="deleteordershipment"),
    
    path("addordershipmentattribute/<int:order_id>/",views.AddOrderShipmentAttributeOrder.as_view(),name="ordershipmentattributeorder"),
    path('editordershipmentattribute/<int:pk>/',views.EditOrderShipmentAttributeOrder.as_view(),name="editordershipmentattributeorder"),
    path("deleteordershipmentattribute/<int:pk>/",views.DeleteView.as_view(model=OrderShipmentAttributes,success_url=reverse_lazy('shopadmin:orderlist'),active_tab="shop",active_link="order"),name="deleteordershipmentattribute"),
    
    path('shipment', views.OrderShipmentView.as_view(),name="shipment"),
    path('shipmentShopadmin', views.OrderShipmentViewShopadmin.as_view(),name="shipmentshopadmin"),
    
]