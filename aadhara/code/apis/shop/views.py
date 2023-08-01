from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions,authentication
from rest_framework import status
from core import choices
from core.models import Pincode
from shop.models import Order,Wishlist,Cart
from django.conf import settings
from shop.mails import order_placed_communication, payment_failed_communication
from shop.shipment.nimbuspost import Nimbuspost

class AddToCart(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        product_id = request.data.get('product_id',False)
        product_option_id = request.data.get('product_option_id',False)
        quantity = int(request.data.get('quantity',1))
        if product_id and product_option_id and quantity > 0 and quantity <= 10:
            try:
                cart = Cart.get_cart(request)
                cart.add_product(product_id,product_option_id,quantity)
                response = Response("Added to Cart", status=status.HTTP_200_OK) 
                response.set_cookie(settings.SESSION_CART_NAME, cart.name)
                return response
            except Exception as e:
                import traceback
                traceback.print_exc()
                return Response("{}".format(e), status=status.HTTP_400_BAD_REQUEST)

        elif product_id and product_option_id and quantity == 0:
            cart = Cart.get_cart(request)
            cart.remove_product(product_id,product_option_id)   
            return Response("Removed from Cart", status=status.HTTP_200_OK)         
            
        return Response("Cart Product Details Required", status=status.HTTP_400_BAD_REQUEST)            

class WishlistAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]

    def post(self, request):
        product_option_id = request.data.get('product_option_id',False)
        user = request.user
        if  product_option_id and user :
            if request.POST.get('delete',False):
                Wishlist.objects.filter(user=user,product_option_id=product_option_id).delete()
                return Response("Removed from Wishlist", status=status.HTTP_200_OK)         
                
            Wishlist.objects.get_or_create(user=user,product_option_id=product_option_id)
            return Response("Added to Wishlist", status=status.HTTP_200_OK)         
            
        return Response("Cart Product Details Required", status=status.HTTP_400_BAD_REQUEST)            




class CreateOrder(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        
        cart = Cart.get_cart(request)
        # print('cart.id',cart.id)
        try:
            if cart.is_eligible_for_checkout():
                order =  cart.place_order()
                data={}
                data['order_id'] = order.id
                data['payment_info'] = order.get_payment_info()
                data['retry_payment_url'] = order.retry_payment_url
                return Response(data, status=status.HTTP_200_OK)         
        except Exception as e:
            import traceback
            # print(traceback.format_exc())
            # print("asldhflkahsdf",e)
            return Response("Something went very wrong.", status=status.HTTP_400_BAD_REQUEST)            


            
        return Response("Your cart is not eligible for checkout at the moment.", status=status.HTTP_400_BAD_REQUEST)            



class UpdateOrderPayment(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        
        try:
            order_id = request.data.get('order_id',False)
            gateway = request.data.get('gateway',1)
            gateway_order_id = request.data.get('gateway_order_id',False)
            gateway_payment_id = request.data.get('gateway_payment_id',False)
            gateway_signature = request.data.get('gateway_signature',False)
            order = Order.objects.filter(pk=order_id).first()
            # print(order,order_id,gateway_payment_id,gateway_order_id,gateway_signature)
            if order and gateway_payment_id and gateway_order_id and gateway_signature:
                d={}
                d['gateway'] = gateway
                d['gateway_order_id'] = gateway_order_id
                d['gateway_signature'] = gateway_signature
                d['gateway_payment_id'] = gateway_payment_id
                order.add_payment(**d)
                if order.is_paid_successfully():
                    request.session['RECENT_ORDER'] = order.id
                    order_placed_communication(order)
                    return Response("Order Placed Successfully", status=status.HTTP_200_OK)
                else:
                    payment_failed_communication(order)
                    return Response("Payment Failed.", status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            print("aslkahsdf",e)
            
        return Response("Request rejected.", status=status.HTTP_400_BAD_REQUEST)            

class Checkserviceability(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self,request):
        data={}
        data['message'] = "No Available"
        pincode = request.data.get('pincode')
        try:
            pd = Pincode.objects.get(pincode=pincode)
        except Exception as e:
            return Response(data,status=status.HTTP_200_OK)
        nmb=Nimbuspost()
        result=nmb.check_pincode_delivery(pincode)
        if result:
            data['message']="Available"
            return Response(data,status=status.HTTP_200_OK)
        return Response(data,status=status.HTTP_200_OK)        