from core.models import Configuration, ContactUs, StaticPage
from core.utils import build_breadcrumb, build_html_head
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import Blog
from taggit.models import Tag


# Create your views here.
def blog_view(request):
    ctx={}
    ctx['breadcrumb']=build_breadcrumb([{'title':'Blogs','text':'Blogs'}])
    ctx['html_head']=build_html_head(title='Blogs', description='Blogs')
    ctx['blogs']=Blog.objects.all()
    return render(request, "storefront/blog/list.html", ctx)

def blog_detail_view(request,id):
    ctx={}
    ctx['breadcrumb']=build_breadcrumb([{'title':'Blogs','url':reverse('blogs:bloglist'),'text':'Blogs'},{'title':'detail','text':'Detail'}])
    ctx['html_head']=build_html_head(title='Blogs', description='Blogs')
    ctx['blog']=Blog.objects.get(id=id)
    ctx['related_blogs']=Blog.objects.exclude(id=id)
    
    return render(request, "storefront/blog/detail.html", ctx)
