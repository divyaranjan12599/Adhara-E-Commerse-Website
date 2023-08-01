from django.db import models
from django.db.models.query import QuerySet
from django.urls.base import reverse
from core import choices
from simple_history.models import HistoricalRecords
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords
from django.utils.text import slugify
from django.conf import settings


# Create your models here.
class SoftDeletionQuerySet(QuerySet):
    def delete(self):
        return super(SoftDeletionQuerySet, self).update(object_status = choices.ObjectStatusChoices.DELETED)

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

class ObjectManager(models.Manager):
    def get_queryset(self):
        return SoftDeletionQuerySet(self.model).filter(object_status=choices.ObjectStatusChoices.ACTIVE)

    def complete(self):
        return super().get_queryset()

class BaseTechvinsModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    object_status = models.SmallIntegerField(choices=choices.ObjectStatusChoices.CHOICES, default=choices.ObjectStatusChoices.ACTIVE)

    # updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,limit_choices_to={'is_staff': True})
    objects = ObjectManager()

    class Meta:
        abstract = True

    def __str__(self):
        value = self.name if hasattr(self,'name') else getattr(self,"id")
        return "{}".format(value)

# def description(instance):
#         return 'Know more about the {} of {}'.format(instance.title,settings.SITE_NAME)

class StaticPage(BaseTechvinsModel):

    title = models.CharField(max_length=200)
    meta_description = models.CharField(max_length=150,blank=True,null=True,help_text="This is for SEO")
    content = RichTextField()
    slug=models.SlugField(max_length=200)
    history = HistoricalRecords()
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.meta_description:
            self.meta_description = 'Know more about the {} of {}'.format(self.title,Configuration.get('SITE_NAME','AADHARA'))
        super(StaticPage, self).save(*args, **kwargs)

    @property
    def edit_url(self):
        return reverse('shopadmin:editstaticpage',args=[self.id])
    
class Configuration(BaseTechvinsModel):
    key = models.CharField(max_length=120,unique=True)
    value = models.CharField(max_length=120)
    editable = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        return "{}".format(self.key)


    @classmethod
    def get(cls,key,default='',editable=True):
        c,created=Configuration.objects.get_or_create(key=key,defaults={'value':default,'editable':editable})
        return c.value

    @property
    def edit_url(self):
        return reverse('shopadmin:editconfiguration',args=[self.id])
    
class NewsletterSubscriber(BaseTechvinsModel):
    email = models.CharField(max_length=200,unique=True)

    @property
    def edit_url(self):
        return reverse('shopadmin:editnewsletter',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deletenewsletter',args=[self.id])


class CityState(BaseTechvinsModel):
    name=models.CharField(max_length=200)
    parent= models.ForeignKey('self',null=True,blank=True, on_delete=models.SET_NULL,related_name="child")
    type = models.SmallIntegerField(choices=choices.CityStateType.CHOICES)

    @property
    def state_name(self):
        if self.type in  [choices.CityStateType.CITY,choices.CityStateType.DISTRICT] and self.parent:
            return self.parent.state_name
        if self.type == choices.CityStateType.STATE:
            return self.name
        return "-"

    @property
    def edit_url(self):
        return reverse('shopadmin:updatecitystate',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deletecitystate',args=[self.id])

    def get_gst_code(self):
        if self.type in  [choices.CityStateType.CITY,choices.CityStateType.DISTRICT] and self.parent:
            return self.parent.get_gst_code()

        if self.type == choices.CityStateType.STATE:
            gst_state_codes ={}
            gst_state_codes['jammu and kashmir']=1
            gst_state_codes['himachal pradesh']=2
            gst_state_codes['punjab']=3
            gst_state_codes['chandigarh']=4
            gst_state_codes['uttarakhand']=5
            gst_state_codes['haryana']=6
            gst_state_codes['delhi']=7
            gst_state_codes['rajasthan']=8
            gst_state_codes['uttar pradesh']=9
            gst_state_codes['bihar']=10
            gst_state_codes['sikkim']=11
            gst_state_codes['arunachal pradesh']=12
            gst_state_codes['nagaland']=13
            gst_state_codes['manipur']=14
            gst_state_codes['mizoram']=15
            gst_state_codes['tripura']=16
            gst_state_codes['meghlaya']=17
            gst_state_codes['assam']=18
            gst_state_codes['west bengal']=19
            gst_state_codes['jharkhand']=20
            gst_state_codes['odisha']=21
            gst_state_codes['chattisgarh']=22
            gst_state_codes['madhya pradesh']=23
            gst_state_codes['gujarat']=24
            gst_state_codes['daman and diu']=26
            gst_state_codes['dadra and nagar haveli']=26
            gst_state_codes['maharashtra']=27
            gst_state_codes['karnataka']=29
            gst_state_codes['goa']=30
            gst_state_codes['lakshwadeep']=31
            gst_state_codes['kerala']=32
            gst_state_codes['tamil nadu']=33
            gst_state_codes['puducherry']=34
            gst_state_codes['andaman and nicobar islands']=35
            gst_state_codes['telangana']=36
            gst_state_codes['andhra pradesh']=37
            gst_state_codes['ladakh']=38

            return gst_state_codes.get(self.name.lower(),-1)
        return -1

class Pincode(models.Model):
    pincode=models.IntegerField()
    city_state = models.ForeignKey(CityState,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return "{}".format(self.pincode)

    @property
    def edit_url(self):
        return reverse('shopadmin:updatepincode',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deletepincode',args=[self.id])

class Promotion(BaseTechvinsModel):
    name=models.CharField(max_length=50)
    enabled = models.BooleanField(default=False)
    url = models.URLField(blank=True)
    message = models.CharField(max_length=120,blank=True)

    def __str__(self):
        return self.name

    @property
    def edit_url(self):
        return reverse('shopadmin:editpromotion',args=[self.id])
    
    @classmethod
    def get(cls,name):
        c,created=Promotion.objects.get_or_create(name=name)
        return c

class HomepageSlider(BaseTechvinsModel):
    name=models.CharField(max_length=50)
    enabled = models.BooleanField(default=False)
    url = models.URLField()
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=120,blank=True)
    button_text = models.CharField(max_length=120)
    priority = models.PositiveSmallIntegerField(default=1,help_text="1 is higher than 2")
    image = models.ImageField(upload_to="upload/homepage/",null=True,max_length=250)
    
    def __str__(self):
        return self.name

    @property
    def edit_url(self):
        return reverse('shopadmin:edithomepageslider',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deletehomepageslider',args=[self.id])     

class TextPlaceholder(BaseTechvinsModel):
    key = models.CharField(max_length=120,unique=True)
    value = models.TextField()
    history = HistoricalRecords()

    def __str__(self):
        return "{}".format(self.key)


    @classmethod
    def get(cls,key,default=0,editable=True):
        c,created=TextPlaceholder.objects.get_or_create(key=key,defaults={'value':default})
        return c.value


class APILog(BaseTechvinsModel):
    url = models.TextField()
    request = models.TextField()
    response = models.TextField()
    status_code = models.SmallIntegerField()

class ContactUs(BaseTechvinsModel):
    name = models.CharField(max_length=200,null=True,blank=True)
    message = models.TextField(max_length=200,blank=True,null=True)
    email = models.CharField(max_length=255)
    mobile = models.BigIntegerField()
    subject = models.CharField(max_length=200,null=True,blank=True)

    @property
    def detail_url(self):
        return reverse('shopadmin:contactusdetail',args=[self.id])
    
class GalleryImage(BaseTechvinsModel):
    title = models.CharField(max_length=200,null=True,blank=True)
    image = models.ImageField(upload_to="upload/homepage/",null=True,max_length=250,help_text="minimum width: 775px")
    priority = models.IntegerField(default=1,help_text="1 is higher than 2")
    
    @classmethod
    def gallery_page(cls):
        return GalleryImage.objects.all().order_by('priority')

    @property
    def edit_url(self):
        return reverse('shopadmin:editgalleryimage',args=[self.id])
    
    @property
    def delete_url(self):
        return reverse('shopadmin:deletegalleryimage',args=[self.id])

