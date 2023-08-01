from rest_framework import serializers
from users.models import User
from ecommerce.jinja_env import img_tag

class ReferralSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['photo','did', 'name','status']

    def get_photo(self,obj):
        url = obj.profile_picture_url() or "assets/images/icons/no-image.png"
        return img_tag(size="100/100", src=url,class_name='profile_image')
        

    def get_status(self,obj):
        return "Active" if obj.is_active else None


class ReferralTreeSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    id = serializers.IntegerField(source="did")
    parent=serializers.IntegerField(source='parent_id')

    class Meta:
        model = User
        fields = ['id','did', 'name','status','image','parent']


    def get_image(self,obj):
    	return obj.profile_picture_url()

    def get_status(self,obj):
        return "Active" if obj.is_active else None