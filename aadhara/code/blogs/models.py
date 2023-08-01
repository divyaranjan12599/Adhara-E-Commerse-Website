from ckeditor.fields import RichTextField
from core.models import BaseTechvinsModel
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from simple_history.models import HistoricalRecords
from users.models import User
from core import choices
from taggit.managers import TaggableManager
# Create your models here.


class Blog(BaseTechvinsModel):
    content = RichTextField()
    title = models.CharField(max_length=200)
    author=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    thumbnail = models.ImageField(upload_to="upload/blog/thumbnail/",null=True)
    priority = models.IntegerField(default=1,help_text="1 is higher than 2")
    publish_status=models.PositiveSmallIntegerField(choices=choices.PublishStatus.CHOICES,default=choices.PublishStatus.DRAFT)
    tags = TaggableManager()


