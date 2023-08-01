from django.conf import settings
from django.utils.crypto import get_random_string
import requests
from core import choices
from .models import OTP,CommunicationLog
from django.core.mail import EmailMultiAlternatives
from core import email_strings, sms_strings
from django.template.loader import render_to_string
from users.models import User
from shop.models import Order
from django.utils.safestring import mark_safe
from django.template.loader import get_template
 
class ComService:
    _SERVICE_URL = settings.MOBILE_SMS_SERVICE
    from_email = settings.FROM_EMAIL

    def generate_otp(self):
        return get_random_string(4, allowed_chars='123456789')

    def get_otp(self,user,otp_type):
        user_otp=OTP.objects.filter(user=user,type=otp_type)
        if user_otp.exists():
            user_otp = user_otp.first()
            return user_otp.otp
        new_otp =self.generate_otp()
        OTP.objects.create(user=user,otp=new_otp,type=otp_type)
        return new_otp


    def send_mail(self,subject,to,text_content, html_content):
        status=False
        try:
            if not isinstance(to, list):
                to = [to]
            msg = EmailMultiAlternatives(subject, text_content, self.from_email, to)
            msg.attach_alternative(html_content, "text/html")
            status=msg.send()
        except:
            print("Dasdfasd, errror")
        self.make_log_entry(to,html_content,choices.CommunicationTypeChooices.EMAIL,status)
        return status

    def make_log_entry(self,to,body,com_type,response):
        CommunicationLog.objects.create(to=to,body=body,type=com_type,response=response)


    def build_email_subject(self,txt):
        return txt

    def send_email_otp(self,user):
        otp = self.get_otp(user,choices.CommunicationTypeChooices.EMAIL)
        subject=self.build_email_subject(email_strings.EMAIL_OTP_SUBJECT)
        to=user
        html_content=render_to_string('mail/user/otp.html', { 'otp': otp })
        text_content=html_content
        return self.send_mail(subject,to,text_content,html_content)

    def send_mobile_otp(self,user):
        try:
            user= int(user)
            otp = self.get_otp(user,choices.CommunicationTypeChooices.SMS)
            # print("sending mobile otp for {} is {}".format(user,otp))
            # message = sms_strings.OTP.format(otp=otp)
            otp_block='{"OTP":' + otp+'}'
            url = self._SERVICE_URL.format(otp_block=otp_block,mobile=user)
            r = requests.get(url=url)
            self.make_log_entry(user,url,choices.CommunicationTypeChooices.SMS,r.content)
            return r.status_code == 200
        except Exception as e:
            # print("Invalid mobile_number",user,e)
            return False

    def send_otp(self,user,otp_type):
        if otp_type == choices.CommunicationTypeChooices.EMAIL:
            return self.send_email_otp(user)
        elif otp_type == choices.CommunicationTypeChooices.SMS:
            return self.send_mobile_otp(user)
        return None
        
    def verify_otp(self,user,otp,otp_type):
        user_otp=OTP.objects.filter(user=user,otp=otp,type=otp_type)
        if user_otp.exists():
            user_otp.delete()
            return True
        return False


    def send_registration_success_mail(self,user):
        subject=self.build_email_subject(email_strings.EMAIL_REGISTRATION_SUCCESS.format(user.id))
        to=user.email
        html_content=render_to_string('mail/user/registration_success.html', { 'name': user.name,'id':user.id, 'email':user.email,'mobile':user.mobile })
        text_content=html_content
        return self.send_mail(subject,to,text_content,html_content)
    
    def send_registration_success_sms(self,user):
        import http.client
        import json
        conn = http.client.HTTPSConnection("api.msg91.com")
        payload = {
            "flow_id" : "5f060124d6fc054cba7ea103",
            "name" : user.name,
            "mobile" : user.mobile,
            "email":user.email,
            "id":user.id
            }

        headers = {
            'authkey': "268738AXE3Y6MQve5edc7384P1",
            'content-type': "application/json"
            }
        conn.request("POST", "/api/v5/flow/", json.dumps(payload), headers)
        res = conn.getresponse()
        data = res.read()

        response = data.decode("utf-8")

        self.make_log_entry(user,payload,choices.CommunicationTypeChooices.SMS,response)
        # return data.status_code == 200
    


    def send_order_placed_mail(self,order):
        subject=self.build_email_subject(email_strings.ORDER_PLACED)
        to=order.user.email
        items = ""
        for product in order.products.all():
            items += mark_safe("<li>{}</li>".format(product.product_option.name))
        htmly = get_template('mail/shop/order_placed.html')
        html_content=render_to_string('mail/shop/order_placed.html', { 'name': order.user.name,'items':items })
        html_content=htmly.render({ 'name': order.user.name,'items':items })
        text_content=html_content
        return self.send_mail(subject,to,text_content,html_content)
    
    def send_order_placed_sms(self,order):
        import http.client
        import json
        conn = http.client.HTTPSConnection("api.msg91.com")

        items = order.products.first().product.name
        if order.products.all().count()>1:
            items += " +{}".format((order.products.all().count()-1))
        
        payload = {
            "flow_id" : "5f0d13bad6fc05069f4add82",
            "mobile" : order.user.mobile,
            "items":items,
            }

        headers = {
            'authkey': "268738AXE3Y6MQve5edc7384P1",
            'content-type': "application/json"
            }
        conn.request("POST", "/api/v5/flow/", json.dumps(payload), headers)
        res = conn.getresponse()
        data = res.read()

        response = data.decode("utf-8")

        self.make_log_entry(order.user,payload,choices.CommunicationTypeChooices.SMS,response)
        # return data.status_code == 200


    def send_password_change_mail(self,user):
        subject=self.build_email_subject(email_strings.EMAIL_REGISTRATION_SUCCESS.format(user.id))
        to=user.email
        html_content=render_to_string('mail/user/password_change.html', { 'name': user.name })
        text_content=html_content
        return self.send_mail(subject,to,text_content,html_content)
    
    def send_password_change_sms(self,user):
        import http.client
        import json
        conn = http.client.HTTPSConnection("api.msg91.com")
        payload = {
            "flow_id" : "5f060124d6fc054cba7ea103",
            "name" : user.name,
            "mobile" : user.mobile,
            "email":user.email,
            "id":user.id
            }

        headers = {
            'authkey': "268738AXE3Y6MQve5edc7384P1",
            'content-type': "application/json"
            }
        conn.request("POST", "/api/v5/flow/", json.dumps(payload), headers)
        res = conn.getresponse()
        data = res.read()

        response = data.decode("utf-8")

        self.make_log_entry(user,payload,choices.CommunicationTypeChooices.SMS,response)
        # return data.status_code == 200

    
    def send_payment_failed_mail(self,order):
        subject=self.build_email_subject(email_strings.ORDER_PLACED)
        to=order.user.email
        items = ""
        for product in order.products.all():
            items += mark_safe("<li>{}</li>".format(product.product_option.name))
        htmly = get_template('mail/shop/order_placed.html')
        html_content=render_to_string('mail/shop/order_placed.html', { 'name': order.user.name,'items':items })
        html_content=htmly.render({ 'name': order.user.name,'items':items })
        text_content=html_content
        return self.send_mail(subject,to,text_content,html_content)
    
    def send_payment_failed_sms(self,order):
        import http.client
        import json
        conn = http.client.HTTPSConnection("api.msg91.com")

        items = order.products.first().product.name
        if order.products.all().count()>1:
            items += " +{}".format((order.products.all().count()-1))
        
        payload = {
            "flow_id" : "5f0d13bad6fc05069f4add82",
            "mobile" : order.user.mobile,
            "items":items,
            }

        headers = {
            'authkey': "268738AXE3Y6MQve5edc7384P1",
            'content-type': "application/json"
            }
        conn.request("POST", "/api/v5/flow/", json.dumps(payload), headers)
        res = conn.getresponse()
        data = res.read()

        response = data.decode("utf-8")

        self.make_log_entry(order.user,payload,choices.CommunicationTypeChooices.SMS,response)
        # return data.status_code == 200
    

# @app.task
def send_registration_success(user_id):
    cs=ComService()
    user = User.objects.get(pk=user_id)
    cs.send_registration_success_mail(user)

    cs.send_registration_success_sms(user)

# @app.task
def send_order_placed(order_id):
    cs=ComService()
    order = Order.objects.get(pk=order_id)
    cs.send_order_placed_mail(order)

    cs.send_order_placed_sms(order)


