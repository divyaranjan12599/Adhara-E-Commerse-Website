from .models import User
from django.db.models import Q

from django.contrib.auth.backends import ModelBackend

class CustomUserBackend(ModelBackend):
    
    def authenticate(self, request, username=None, password=None):
        try:
            mobile=int(username)
            email=str(username)
        except:
            mobile=0
            email=str(username)
        try:
             user = User.objects.get(
                 Q(email=email) | Q(mobile=mobile)
             )
             pwd_valid = user.check_password(password)
             if pwd_valid:            
                 return user
             return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None