from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from .serializers import PincodeSerializer
from core import choices
from core.models import Pincode

class CityStateByPin(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
    
        result = {}
        try:
            pincode = int(request.GET.get('pincode','0'))
            if pincode:
                cities = Pincode.objects.filter(pincode=pincode).first()
                data = PincodeSerializer(cities,many=False).data
                return Response(data, status=status.HTTP_200_OK)
        except:
            print("Non parsed pincode",request.GET.get('pincode','0'))
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


