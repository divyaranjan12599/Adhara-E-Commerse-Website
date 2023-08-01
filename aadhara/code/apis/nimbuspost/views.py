from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions,authentication

from rest_framework import status
from shop.models import Order
from shop.shipment.nimbuspost import Nimbuspost


class CreateOrder(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]


    def get(self, request):
        result = {}
        try:
            order_id = int(request.GET.get('order_id','0'))
            order = Order.objects.filter(id=order_id).first()
            if order:
                data = Nimbuspost()
                result=data.create_order(order)
                data=result.get('data')
                return Response("API Response Send request {}".format(data.get('status')), status=status.HTTP_200_OK)
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
                data = Nimbuspost()
                result=data.request_pickup([order.id])
                return Response("Pickup Requested", status=status.HTTP_200_OK)
        except Exception as e:
            print("Server Error shipppp",e)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class TruckOrderStatus(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]

    def get(self, request):
        result = {}
        try:
            order_id = int(request.GET.get('order_id','0'))
            order = Order.objects.filter(id=order_id).first()
            if order:
                data = Nimbuspost()
                result=data.track_order_status([order.id])
                msg="Shipment Status {},Created Datetime {},Message {}".format(result.get('status_message'),result.get('event_time'),result.get('message'))
                return Response(msg, status=status.HTTP_200_OK)
        except Exception as e:
            print("Server Error shipppp",e)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)





