import razorpay
from django.conf import settings 
class RazorpayService:

    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))

    def create_order(self,order_amount=0,order_receipt=""):
        order_currency = 'INR'
        data = {}
        data['amount'] = order_amount
        data['currency'] = order_currency
        data['receipt'] = order_receipt
        data['payment_capture'] = 1
        # response = self.client.order.create(amount=order_amount, currency=order_currency, receipt=order_receipt, notes="", payment_capture='0')
        response = self.client.order.create(data)
        # print('razorpay order created',response)
        return response.get('id')


    def check_order_status(self,order_id="order_Ero2I7oAA8dXHo"):
        #order_Ero2I7oAA8dXHo

        order_payment = self.client.order.payments(order_id)
        return order_payment

    def verify_payment(self,order_payment):
        try:
           
            signature_verified = self.get_signature_status(order_payment)           
            payment_status = self.get_payment_status(order_payment)

            return signature_verified is None and payment_status
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            
            # print("asdfasd",e)
        return False

    def get_signature_status(self,order_payment):
        d={}
        d['razorpay_payment_id'] = order_payment.gateway_payment_id
        d['razorpay_order_id'] = order_payment.gateway_order_id
        d['razorpay_signature'] = order_payment.gateway_signature
        result = self.client.utility.verify_payment_signature(d)
        # print("signature_status for {} : {}".format(order_payment.id,result))

    def get_payment_status(self,order_payment):
        payment_id,amount=order_payment.gateway_payment_id,order_payment.order.get_total_amount()
        payment_detail = self.client.payment.fetch(payment_id)
        # print("payment_details for {} : {}".format(order_payment.id,payment_detail))
        return payment_detail.get('status') == 'captured' and int(payment_detail.get('amount')) == amount