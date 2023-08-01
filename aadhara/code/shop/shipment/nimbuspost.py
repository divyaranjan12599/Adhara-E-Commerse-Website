import requests
import json

from requests.api import head
from shop.models import OrderShipmentAttributes
from core import choices
from ecommerce.settings import PICKUP_WAREHOUSE_NAME,PICKUP_NAME,PICKUP_CITY,PICKUP_ADDRESS,PICKUP_PHONE_NO,PICKUP_PINCODE,PICKUP_STATE
class Nimbuspost:
    def __init__(self):
        self._TOKEN = ""

    def _hit_api(self,url,payload={},method="POST"):
        headers = {
        "Content-Type" : "application/json",
        "Authorization" : 'Bearer {}'.format(self._TOKEN)
        }
        data=json.dumps(payload)
        response = requests.request(method, url, headers=headers, data =data)
        return json.loads(response.text)

    def check_pincode_delivery(self,delivery_pincode):
        url = "https://api.nimbuspost.com/v1/courier/serviceability"
        payload={}
        payload['origin'] = "302021"
        payload['destination'] = delivery_pincode
        payload['payment_type']="prepaid"
        if not self._TOKEN:
            self._get_token()
        result = self._hit_api(url,payload=payload,method="POST")
        return result.get('status') and len(result.get('data'))>0
    
    def _get_token(self):
        url="https://api.nimbuspost.com/v1/users/login"
        payload={}
        payload['email'] = "shreyaadesigns@gmail.com"
        payload['password'] = "12345678"
        token = self._hit_api(url,payload=payload)
        self._TOKEN = token.get('data')
        
    def create_order(self,order):
        
        if not self._TOKEN:
            self._get_token()
        url = "https://api.nimbuspost.com/v1/shipments"
        payload={}
        payload['order_number'] = order.id
        payload['payment_type'] =  "prepaid"
        payload['package_weight'] = 15
        payload['package_length'] = 15
        payload['package_breadth'] = 15
        payload['package_height'] =15
       
        payload['order_amount'] = order.total_price
        payload['consignee'] = self.get_shipping_address(order) 
        payload['pickup'] = self.get_pickup_address()
        payload['order_items']=self.get_order_product(order)
              
        result = self._hit_api(url,payload=payload)
        # print("##"*10,"result","##"*10)
        # print(result)
        # print("##"*10,"result","##"*10)
        data=result.get('data')
        if result.get('status'):
            OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.PROVIDER,value="Nimbuspost")
            OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.ORDER_ID,value=data.get('order_id'))
            OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.SHIPMENT_ID,value=data.get('shipment_id'))
            OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.AWB_NO,value=data.get('awb_number'))
            OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.COURIER_ID,value=data.get('courier_id'))
            OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.COURIER_NAME,value=data.get('courier_name'))
            OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.STATUS,value=data.get('status'))
            OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.ADDITIONAL_INFO,value=data.get('additional_info'))
            OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.PAYMENT_TYPE,value=data.get('payment_type'))
            OrderShipmentAttributes.objects.create(order=order,key=choices.ShipmentProviderAttributes.LABEL,value=data.get('label'))
        return result
    
    def get_shipping_address(self,order):
        
        d={}
        d['name'] = order.name
        d['address'] = order.shipping_address
        d['city'] = order.shipping_pincode.city_state.name
        d['state'] = order.shipping_pincode.city_state.state_name
        d['pincode']= order.shipping_pincode.pincode
        d['phone']= order.mobile
        return d
    
    def get_pickup_address(self):
        d={}
        d['warehouse_name'] = PICKUP_WAREHOUSE_NAME
        d['name'] = PICKUP_NAME
        d['address'] = PICKUP_ADDRESS
        d['city'] = PICKUP_CITY
        d['state'] = PICKUP_STATE
        d['pincode'] = PICKUP_PINCODE
        d['phone'] = PICKUP_PHONE_NO
        return d
    
    def get_order_product(self,order):
        l=[]
        order_product=order.products.all()
        for op in order_product:
            d={}
            d['name']=op.name
            d['qty']=op.quantity
            d['price']=op.total_price
            d['sku']=op.product.sku
            l.append(d)
        return l
            
    def request_pickup(self,orders):
        if not self._TOKEN:
            self._get_token()
        # url = "https://ship.nimbuspost.com/api/shipments/pickups"
        url=""
        payload={}
        order_id=OrderShipmentAttributes.objects.filter(order__in=orders,key=choices.ShipmentProviderAttributes.ORDER_ID).last().value
        payload['ids']=[order_id]
        result = self._hit_api(url,payload=payload)
        return result
    
    def track_order_status(self,orders):
        if not self._TOKEN:
            self._get_token()
        payload={}
        awb_number=OrderShipmentAttributes.objects.filter(order__in=orders,key=choices.ShipmentProviderAttributes.AWB_NO).last().value

        url="https://api.nimbuspost.com/v1/shipments/track/{}".format(awb_number)

        result = self._hit_api(url,payload=payload,method="GET")

        return self.clean_track_order_status(result)
        
    def clean_track_order_status(self,result):
        l={}
        data = result.get('data')
        if len(data.get('history')) == 0:
            l['status_message']="Check after some time"
            l['event_time']=''
            l['message']=''
            return l
        history=data.get('history')[0]
        status_code = history.get('status_code')
        if status_code == "PP":
            l['status_message']="Pending Pickup"
        elif status_code == "IT":
            l['status_message']="In Transit"
        elif status_code == "EX":
            l['status_message']="Exception"
        elif status_code == "OFD":
            l['status_message']="Out For Delivery"  
        elif status_code == "DL":
            l['status_message']="Delivered"
        elif status_code == "RT":
            l['status_message']="RTO"
        elif status_code == "RT-IT":
            l['status_message']="RTO In Transit"
        elif status_code == "RT-DL":
            l['status_message']="RTO Delivered"
        l['event_time']=history.get('event_time')
        l['message']=history.get('message')
        return l
                
            