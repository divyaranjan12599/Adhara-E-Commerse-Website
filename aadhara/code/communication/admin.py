from django.contrib import admin
from .models import CommunicationLog,OTP


# Register your models here.

admin.site.register(OTP)
admin.site.register(CommunicationLog)