class ObjectStatusChoices(object):
    ACTIVE=1
    DELETED=0
    CHOICES = (
        (DELETED, 'Deleted'),
        (ACTIVE, 'Active')
    )


class CityStateType(object):
    COUNTRY=1
    STATE=2
    DISTRICT=3
    CITY=4
    CHOICES = (
        (COUNTRY, 'Country'),
        (STATE, 'State'),
        (DISTRICT, 'District'),
        (CITY, 'City')
    )
class CommunicationTypeChooices(object):
    EMAIL=1
    SMS=2
    CHOICES = (
        (EMAIL, 'Email'),
        (SMS, 'SMS')
    )



class CartStatus(object):
    FRESH=0
    PAID=10
    CHOICES = (
        (FRESH, 'Fresh'),
        (PAID, 'Paid')
    )

class DiscountCategoryType(object):
    ALL=0
    USER_GROUP=10
    CHOICES = (
        (ALL, 'Applied to All Users'),
        (USER_GROUP, 'Applied to User Groups #coming soon')
    )

class DiscountType(object):
    PERCENTAGE=0
    CHOICES = (
        (PERCENTAGE, 'Percentage'),
    )

class OrderStatus(object):
    PENDING = 0
    PLACED = 10
    PROCESSING = 20
    SHIPPED = 30
    COMPLETE = 40
    CANCELED = 50

    CHOICES = (
        (PENDING, 'Pending'),
        (PLACED, 'Placed'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (COMPLETE, 'Complete'),
        (CANCELED, 'Canceled'),
    )



class OrderPaymentStatus(object):
    PENDING = 0
    PROCESSING = 10
    APPROVED = 20
    REVERSED = 30
    FAILED = 40

    CHOICES = (
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (APPROVED, 'Approved'),
        (REVERSED, 'Reversed'),
        (FAILED, 'Failed'),
    )

class ShipmentStatus(object):
    NONE = 0

    PROCESSING = 10
    DISPATCHED = 20
    DELIVERED = 30

    CHOICES = (
        (NONE, 'None'),
        (PROCESSING, 'Processing'),
        (DISPATCHED, 'Dispatched'),
        (DELIVERED, 'Delivered'),
    )
class StatusChoices(object):
    ENABLED=1
    DISABLED=0
    CHOICES = (
        (ENABLED, 'Enabled'),
        (DISABLED, 'Disabled')
    )
class GatewayChoices(object):
    RAZORPAY=1
    CHOICES = (
        (RAZORPAY, 'Razorpay'),
    )

class YesNoChoices(object):
    NO=1
    YES=2
    CHOICES = (
        (YES, 'Yes'),
        (NO, 'No'),
    )
class ShipmentProviderAttributes(object):
    PROVIDER=0
    ORDER_ID=1
    SHIPMENT_ID=2
    AWB_NO =3
    COURIER_NAME=4
    LENGTH=5
    WIDTH=6
    HEIGHT=7
    WEIGHT=8
    COURIER_ID=10
    STATUS=11
    ADDITIONAL_INFO=12
    PAYMENT_TYPE=13
    LABEL=14
    CHOICES = (
        (PROVIDER, 'Provider'),
        (ORDER_ID, 'Order Id'),
        (SHIPMENT_ID, 'Shipment Id'),
        (AWB_NO, 'AWB No'),
        (COURIER_NAME,'Courier Name'),
        (LENGTH,'Length in cms'),
        (WIDTH,'Width in cms'),
        (HEIGHT,'Height in cms'),
        (WEIGHT,'Weight in grams'),
        (COURIER_ID,"Courier id"),
        (STATUS,"Shipment order status"),
        (ADDITIONAL_INFO,"Additional info of shipment Order"),
        (PAYMENT_TYPE,"Payment type"),
        (LABEL,"Shipment Order Shlip link"),
    )


class PublishStatus(object):
    DRAFT=10
    PUBLISHED=20
    HIDDEN=30
    CHOICES=(
        (DRAFT,'Draft'),
        (PUBLISHED,'Published'),
        (HIDDEN,'Hidden')
    )

class DiscountType(object):
    PERCENTAGE=1
    ABSOLUTERUPEES=2
    CHOICES=(
        (PERCENTAGE,'Percentage'),
        (ABSOLUTERUPEES,'Absolute Rupees')
    )
    
class DiscountCouponType(object):
    FIRST_PURCHASE=1
    ALL_PURCHASES=2
    CHOICES=(
        (FIRST_PURCHASE,'First time purchases'),
        (ALL_PURCHASES,'All purchases')
        )