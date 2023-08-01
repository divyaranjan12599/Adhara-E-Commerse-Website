from users.models import User
from shop.models import Order
#from ecommerce.celery import app
from communication.com_service import ComService
from django.conf import settings
import math
from ecommerce.celery import app

@app.task
def check_designation_change(order_id):
    order=  Order.objects.get(pk=order_id)
    

@app.task
def order_placed_task(order_id):
    order=Order.objects.get(pk=order_id)
    cs=ComService()
    cs.send_order_placed_mail(order)
    cs.send_order_placed_sms(order)


@app.task
def registration_success_task(user_id):
    user=User.objects.get(pk=user_id)
    cs=ComService()
    cs.send_registration_success_mail(user)
    cs.send_registration_success_sms(user)


@app.task
def password_change_task(user_id):
    user=User.objects.get(pk=user_id)
    cs=ComService()
    cs.send_password_change_mail(user)
    cs.send_password_change_sms(user)


@app.task
def payment_failed_task(order_id):
    order=Order.objects.get(pk=order_id)
    cs=ComService()
    cs.send_payment_failed_mail(order)
    cs.send_payment_failed_sms(order)