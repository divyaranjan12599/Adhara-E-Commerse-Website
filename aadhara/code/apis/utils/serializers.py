from rest_framework import serializers
from core.models import Pincode

class PincodeSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="city_state.name")
    state = serializers.CharField(source="city_state.parent.name")
    city_id = serializers.IntegerField(source="city_state.id")
    state_id = serializers.IntegerField(source="city_state.parent.id")
    
    class Meta:
        model = Pincode
        fields = ['pincode', 'city','state', 'city_id','state_id']

    