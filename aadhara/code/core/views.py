import json

from django.contrib.sitemaps import Sitemap
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext as _
from shop.models import HomepageCategory, Product

from core import choices
from core.admin import GalleryImageAdmin
from core.models import (Configuration, ContactUs, GalleryImage,
                         HomepageSlider, NewsletterSubscriber, StaticPage)
from core.utils import build_breadcrumb, build_html_head


def homepage(request):
    ctx={}
    title = Configuration.get('HOME_PAGE_TITLE')
    description = Configuration.get('HOME_PAGE_DESCRIPTION')
    ctx['html_head']=build_html_head(title=title, description=description)
    ctx['homepage_sliders'] = HomepageSlider.objects.filter(enabled=True).order_by('priority') 
    ctx['homepage_categories'] = HomepageCategory.objects.filter(enabled=True).order_by('priority') 
    ctx['latest_products'] = Product.objects.filter(status=choices.StatusChoices.ENABLED).order_by('-modified')[:5]
    
    return render(request, 'storefront/home.html',ctx)

def privacy_policy(request):
    return render(request,'privacy_policy.html')

def static_pages(request,static_page):
    # print(static_page)
    ctx = {}
    #TODO
    #GET PAGE OBJECT by page slug
    page = get_object_or_404(StaticPage,slug=static_page)
    ctx['breadcrumb']=build_breadcrumb([{'title':page.title,'text':page.title}]) #this is for breadcrumb
    ctx['html_head']=build_html_head(title=page.title, description=page.meta_description) #this is for html head
    ctx['title'] = page.title #this is for h1 of page
    ctx['page'] = page
    return render(request, "storefront/static_page.html", ctx)   


def subscribe(request):
    data={}
    message="Please provide your mail for latest update and be the first one to know."
    if request.method == "POST":
        email = request.POST.get('email')
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
            data['close_popup'] = True
            message = "Thank you!"
    data['message']=message
    return HttpResponse(json.dumps(data),content_type="application/json")



def contact_us(request):
    ctx = {}
    if request.method == "POST":
        name=request.POST.get('name',False)
        mobile=request.POST.get('phone',False)
        email=request.POST.get('email',False)
        subject=request.POST.get('subject',False)
        message=request.POST.get('message',False)
        if email and mobile:
            ContactUs.objects.get_or_create(email=email,name=name,mobile=mobile,subject=subject,message=message)
            ctx['message'] = "Thank you, We will get back to you soon"
    ctx['breadcrumb']=build_breadcrumb([{'title':'Contact Us','text':'Contact Us'}])
    ctx['html_head']=build_html_head(title='Contact Us', description='Contact Us Page')
    return render(request, "storefront/contact_us.html", ctx)   

def gallery_view(request):
    ctx = {}
    ctx['breadcrumb']=build_breadcrumb([{'title':'Gallery','text':'Gallery'}])
    ctx['html_head']=build_html_head(title='Gallery', description='Gallery Page')
    ctx['images']=GalleryImage.gallery_page()
    return render(request, "storefront/gallery.html", ctx)   



class ProductSitemap(Sitemap):
    changefreq= "daily"
    priority = 0.7   
    protocol="https"

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return obj.url()
   
