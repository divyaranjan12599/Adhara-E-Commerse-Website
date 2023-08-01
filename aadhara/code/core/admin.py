from django.contrib import admin
from django.db.models import fields
from .models import ( Configuration, ContactUs,StaticPage,Promotion,
    HomepageSlider,NewsletterSubscriber,Pincode,CityState,
    GalleryImage)


class ConfigurationAdmin(admin.ModelAdmin):
    readonly_fields = ('created','modified','key')
    fields = ['created','modified','key','value']
    date_hierarchy = 'created'
    list_display = ['id', 'key','value','created','modified']
    sortable_by=['id', 'key','created']
    ordering = ['key']
    # list_editable=['name','email']
    list_filter = ('modified','created')
    search_fields=['key','value']
    list_display_links=['id','key']

    def get_queryset(self, request):
        qs = super(ConfigurationAdmin, self).get_queryset(request)
        return qs.filter(editable=True)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class PromotionAdmin(admin.ModelAdmin):
    readonly_fields = ('name',)
    fields = ['name','url','message','enabled']
    date_hierarchy = 'created'
    list_display = ['id', 'name','message','url','enabled','created','modified']
    sortable_by=['id', 'name','created']
    ordering = ['name']
    # list_editable=['name','email']
    list_filter = ('modified','created')
    search_fields=['name','message','url']
    list_display_links=['id','name']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

class StaticPageAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)
    fields = ['slug','title','meta_description','content']
    date_hierarchy = 'modified'
    list_display = ['id', 'title','modified']
    sortable_by=['id', 'title','modified']
    ordering = ['title']
    # list_editable=['name','email']
    list_filter = ('modified','created')
    search_fields=['title','meta_description','content']
    list_display_links=['id','title']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class HomepageSliderAdmin(admin.ModelAdmin):
    # readonly_fields = ('name',)
    fields = ['name','url','title','subtitle','button_text','enabled','priority','image']
    date_hierarchy = 'created'
    list_display = ['id', 'name','title','button_text','priority','enabled','created','modified']
    sortable_by=['id', 'name','created','priority']
    ordering = ['name']
    # list_editable=['name','email']
    list_filter = ('modified','created')
    search_fields=['name','title','url']
    list_display_links=['id','name']


class GalleryImageAdmin(admin.ModelAdmin):
    # readonly_fields = ('name',)
    fields = ['title','image','priority']
    date_hierarchy = 'created'
    list_display = ['id', 'title','priority']
    sortable_by=['id', 'title']
    ordering = ['priority']
    # list_editable=['name','email']
    list_filter = ('modified','created')
    search_fields=['name','title']
    list_display_links=['id','title']

class PincodeAdmin(admin.ModelAdmin):
    list_display=['pincode','city_state']
    search_fields=['pincode']


# Register your models here.

admin.site.register(Configuration,ConfigurationAdmin)
admin.site.register(StaticPage,StaticPageAdmin)
admin.site.register(Promotion,PromotionAdmin)
admin.site.register(HomepageSlider,HomepageSliderAdmin)
admin.site.register(NewsletterSubscriber)
admin.site.register(Pincode,PincodeAdmin)
admin.site.register(ContactUs)
admin.site.register(CityState)
admin.site.register(GalleryImage,GalleryImageAdmin)



try:
    StaticPage.objects.get_or_create(slug="about-us",defaults={'title':"About Us",'content':"Content of page"})
    StaticPage.objects.get_or_create(slug="terms-and-conditions",defaults={'title':"Terms and Conditions",'content':"Content of page"})
    StaticPage.objects.get_or_create(slug="privacy-policy",defaults={'title':"Privacy policy",'content':"Privacy Policy"})
    StaticPage.objects.get_or_create(slug="return-policy",defaults={'title':"Order and Return policy",'content':"Privacy Policy"})
except Exception as e:
    # print(e)
    pass