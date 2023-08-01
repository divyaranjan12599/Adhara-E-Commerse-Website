from django.conf import settings
from .tasks import order_placed_task, registration_success_task, password_change_task, payment_failed_task

def order_placed_communication(order):
    if settings.DEBUG:
        order_placed_task(order.id)
    else:
        order_placed_task.delay(order.id)

def registration_success_communication(user):
    if settings.DEBUG:
        registration_success_task(user.id)
    else:
        registration_success_task.delay(user.id)

def password_change_communication(user):
    if settings.DEBUG:
        password_change_task(user.id)
    else:
        password_change_task.delay(user.id)

def payment_failed_communication(user):
    if settings.DEBUG:
        payment_failed_task(user.id)
    else:
        payment_failed_task.delay(user.id)