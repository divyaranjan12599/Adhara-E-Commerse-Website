import datetime
import random
from django.db.models import Q
from django.db import models
from django.contrib import auth
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import UserManager
from django.conf import settings
from core import choices
from core.models import BaseTechvinsModel,CityState,Pincode
from datetime import datetime


class PermissionsMixin(models.Model):
    """
    A mixin class that adds the fields and methods necessary to support
    Django's Group and Permission model using the ModelBackend.
    """
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_(
            'Designates that this user has all permissions without'
            'explicitly assigning them.'
        ),
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_groups_set",
        related_query_name="goognu_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_permissions_set",
        related_query_name="goognu_user",
    )

    class Meta:
        abstract = True

    def get_group_permissions(self, obj=None):
        """
        Returns a list of permission strings that this user has through their
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)


def _user_get_all_permissions(user, obj):
    permissions = set()
    for backend in auth.get_backends():
        if hasattr(backend, "get_all_permissions"):
            permissions.update(backend.get_all_permissions(user, obj))
    return permissions


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_perm'):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_module_perms'):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                return True
        except PermissionDenied:
            return False
    return False

def filter_user_queryset_by_hierarchy(user, queryset,filter_on='assign_to_user__in'):

    if user.is_superuser:
        return queryset
    else:
        all_childrens = user.get_all_child
        return queryset.filter(**{filter_on:all_childrens})


class UserManager(BaseUserManager):
    def create_user(self, email, name, mobile,password=None):
        
        user = self.model(name=name,mobile=mobile,email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, mobile,password):
        user = self.create_user(
            email=email, password=password, name=name,mobile=mobile)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user




class User(AbstractBaseUser,BaseTechvinsModel, PermissionsMixin):
    name = models.CharField('Full Name',max_length=255,null=True,blank=True)
    email = models.EmailField(max_length=255,unique=True)
    mobile=models.BigIntegerField()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','mobile']

    

    def __str__(self):
        return "{}".format(self.name)
        
    def has_module_perms(self, app_label):
        return True


    def get_short_name(self):
        return self.name

    def is_member(self, group_name):
        if self.groups.filter(name__iexact=group_name).exists():
            return True
        return False

    def wishlist(self):
        from shop.models import Wishlist
        return Wishlist.objects.filter(user=self).order_by('-id')
        
    def can_view_admin_actions(self):
        return self.is_superuser
        
    @classmethod
    def exists(cls,email=None,mobile=None):
        if email:
            return User.objects.filter(email=email).exists()
        if mobile:
            return User.objects.filter(mobile=mobile).exists()
        return False

class Address(BaseTechvinsModel):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    address = models.CharField(max_length=512)
    city = models.ForeignKey(CityState,on_delete=models.CASCADE,related_name='city')
    state = models.ForeignKey(CityState,on_delete=models.CASCADE,related_name='state')
    pincode = models.ForeignKey(Pincode,on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    
    default = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile', 'name']

    def one_line(self):
        if self.id:
            return "{}, {}, {}, {} - {}".format(self.name,self.address,self.city.name,self.state.name,self.pincode.pincode)
        return "-"

    @classmethod
    def get(cls, request):
        address = None
        if request.user.is_authenticated:
            address = Address.objects.filter(user=request.user).last()

        return address or Address()