from django.conf import settings 
from core import choices
from datetime import datetime,timedelta
import requests
import json
from core import choices
from shop.models import OrderShipmentAttributes
from core.models import APILog
'''
from shop.shipment.shiprocket import *
rocket=ShipRocketService()
token=rocket._get_token()
rocket.all_orders()
'''
class ShipRocketService:
    def __init__(self):
        self._TOKEN = ""

    def _hit_api(self,url,payload={},method="POST"):
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(self._TOKEN)
        }
        data=json.dumps(payload)
        response = requests.request(method, url, headers=headers, data =data)
        APILog.objects.create(url=url,
            request=data,
            response=response.content,
            status_code=response.status_code)
        # print(response.content)
        return json.loads(response.text)
        
    def _get_token(self):
        url="https://apiv2.shiprocket.in/v1/external/auth/login"
        payload={}
        payload['email'] = settings.SHIPROCKET_API_EMAIL
        payload['password']=settings.SHIPROCKET_API_PASSWORD
        token = self._hit_api(url,payload=payload)
        self._TOKEN = token.get('token')

    def all_orders(self):
        url="https://apiv2.shiprocket.in/v1/external/orders"
        orders = self._hit_api(url,method="GET")
        for o in orders.get('data'):
            print(o)


    def _get_order_items(self,order):
        lst=[]
        for order_product in order.products.all():
            item = {}
            item['name'] = order_product.product.name
            item['sku'] =order_product.product.sku
            item['units'] = order_product.quantity
            item['selling_price'] = order_product.total_price
            item['discount'] = order_product.discount_amount
            lst.append(item)
        return lst

    def create_order(self,order):
        '''
from shop.shipment.shiprocket import *
rocket=ShipRocketService()
token=rocket._get_token()
order = Order.objects.last()
rocket.create_order(order)
        '''

        if not self._TOKEN:
            self._get_token()
        url = "https://apiv2.shiprocket.in/v1/external/orders/create/adhoc"
        payload={}
        payload['order_id'] = order.id #224477
        payload['order_date'] = order.created.strftime(settings.DATE_TIME_FORMAT)
        payload['pickup_location'] ="Primary" 
        payload['billing_customer_name'] = order.user.name.rsplit(' ', 1)[0]
        payload['billing_last_name'] = order.user.name.rsplit(' ', 1)[1]
        payload['billing_city']= order.shipping_pincode.city_state.name
        payload['billing_pincode']= order.shipping_pincode.pincode
        payload['billing_state']= order.shipping_pincode.city_state.state_name
        payload['billing_address'] = order.billing_address

        payload['billing_country']="India"
        payload['billing_email']=order.user.email
        payload['billing_phone']=order.user.mobile
        payload['shipping_is_billing']= 1
        payload['order_items'] = self._get_order_items(order)
        payload['payment_method'] =  "Prepaid" #Prepaid or COD
        payload['sub_total']= order.total_price
        payload['length'] = order.shipping_length()
        payload['breadth'] = order.shipping_width()
        payload['height']=order.shipping_height()
        payload['weight']=round(int(order.shipping_weight())/1000,3) #gm to kg
        # print(payload)
        result = self._hit_api(url,payload=payload)
        # print("##"*10,"result","##"*10)
        # print(result)
        # print("##"*10,"result","##"*10)
        order_id = result.get('order_id')
        shipment_id = result.get('shipment_id')
        OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.PROVIDER,value="Shiprocket")
        OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.ORDER_ID,value=order_id)
        OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.SHIPMENT_ID,value=shipment_id)

        return result

    def generated_awb(self,order):
        '''
from shop.shipment.shiprocket import *
rocket=ShipRocketService()
token=rocket._get_token()
order = Order.objects.last()
rocket.generated_awb(order)
        '''
        if not self._TOKEN:
            self._get_token()
        url = "https://apiv2.shiprocket.in/v1/external/courier/assign/awb"
        payload={}
        shipment_id=OrderShipmentAttributes.objects.filter(order=order,key=choices.ShipmentProviderAttributes.SHIPMENT_ID).last().value
        payload['shipment_id'] =shipment_id
        result = self._hit_api(url,payload=payload)

        awb = result.get('response').get('data').get('awb_code')
        courier_name = result.get('response').get('data').get('courier_name')
        OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.AWB_NO,value=awb)
        OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.COURIER_NAME,value=courier_name)
        return result
    
    def request_pickup(self,orders):
        if not self._TOKEN:
            self._get_token()
        url = "https://apiv2.shiprocket.in/v1/external/courier/generate/pickup"
        payload={}
        shipment_id=OrderShipmentAttributes.objects.filter(order__in=orders,key=choices.ShipmentProviderAttributes.SHIPMENT_ID).last().value
        payload['shipment_id']=shipment_id
        result = self._hit_api(url,payload=payload)
        return result

    def check_pincode_delivery(self,pickup_pincode,delivery_pincode):
        '''
from shop.shipment.shiprocket import *
rocket=ShipRocketService()
token=rocket._get_token()
rocket.check_pincode_delivery("302012","122003")
        '''

        url = "https://apiv2.shiprocket.in/v1/external/courier/serviceability/"
        payload={}
        payload['pickup_postcode'] = pickup_pincode
        payload['delivery_postcode'] = delivery_pincode
        payload['weight'] = "1"
        payload['cod']=0
        result = self._hit_api(url,payload=payload,method="GET")
        return len(result.get('data').get('available_courier_companies')) > 0