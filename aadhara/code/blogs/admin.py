from django.contrib import admin
from .models import Blog
# Register your models here.


class BlogAdmin(admin.ModelAdmin):
    readonly_fields = ('created','author',)
    fields = ['title','content','thumbnail','priority','tags']
    date_hierarchy = 'created'
    list_display = ['id', 'title','author','priority']
    sortable_by=['id', 'title']
    ordering = ['priority']
    # list_editable=['name','email']
    list_filter = ('modified','created')
    search_fields=['content','title']
    list_display_links=['id','title']

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super().save_model(request, obj, form, change)



admin.site.register(Blog,BlogAdmin)