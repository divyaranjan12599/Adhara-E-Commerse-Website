from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions,authentication

from rest_framework import status
from core import choices
from core.models import Pincode
from shop.models import Order
from shop.shipment.shiprocket import ShipRocketService

class CreateOrder(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]


    def get(self, request):
        result = {}
        try:
            order_id = int(request.GET.get('order_id','0'))
            order = Order.objects.filter(id=order_id).first()
            if order:
                data = ShipRocketService()
                result=data.create_order(order)
                return Response("API Response:{}".format(result.get('status')), status=status.HTTP_200_OK)
        except Exception as e:
            print("Server Error shipppp",e)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)



class GenerateAWB(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]


    def get(self, request):
        result = {}
        try:
            order_id = int(request.GET.get('order_id','0'))
            order = Order.objects.filter(id=order_id).first()
            if order:
                data = ShipRocketService()
                result=data.generated_awb(order)
                awb = result.get('response').get('data').get('awb_code')
                courier_name = result.get('response').get('data').get('courier_name')
        
                return Response("Courier :{}, Tracking No: {}".format(courier_name,awb), status=status.HTTP_200_OK)
        except Exception as e:
            print("Server Error shipppp",e)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class RequestPickup(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]


    def get(self, request):
        result = {}
        try:
            order_id = int(request.GET.get('order_id','0'))
            order = Order.objects.filter(id=order_id).first()
            if order:
                data = ShipRocketService()
                result=data.request_pickup([order.id])
                
                return Response("Pickup Requested", status=status.HTTP_200_OK)
        except Exception as e:
            print("Server Error shipppp",e)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class CancelOrder(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]


    def get(self, request):
        result = {}
        try:
            order_id = int(request.GET.get('order_id','0'))
            order = Order.objects.filter(id=order_id).first()
            if order:
                data = ShipRocketService()
                result=data.request_pickup([order.id])
                
                return Response("Pickup Requested", status=status.HTTP_200_OK)
        except Exception as e:
            print("Server Error shipppp",e)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

