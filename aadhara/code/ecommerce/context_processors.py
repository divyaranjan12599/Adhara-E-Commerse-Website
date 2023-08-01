from core.models import Promotion,Configuration
# from core.models import HomepageCategory
from core.models import CityState
from core import choices 
from shop.models import Category, Product,Cart,HomepageCategory
import random
from datetime import datetime

def  mega_menu():
    from shop.models import Category
    return Category.objects.filter(parent__isnull=True).order_by('priority')
    
def globals(request):
        
    kwargs = {
        'header_promotion': Promotion.get('HEADER_PROMOTION'),
        'site_name':Configuration.get('SITE_NAME','AADHARA'),
        'cart':Cart.get_cart(request,create=False),
        'mega_menu_categories':mega_menu(),
        #FOOTER
        'contact_address':Configuration.get('CONTACT_ADDRESS','Contact Address'),
        'contact_mobile':Configuration.get('CONTACT_MOBILE','9876544321'),
        'contact_email':Configuration.get('CONTACT_EMAIL','contact@email.com'),
        'social_facebook':Configuration.get('SOCIAL_FACEBOOK','facebook.com'),
        'social_twitter':Configuration.get('SOCIAL_TWITTER','twitter.com'),
        'social_instagram':Configuration.get('SOCIAL_INSTAGRAM','instagram.com'),
        'social_linkedin':Configuration.get('SOCIAL_LINKEDIN','linkedin.com'),
        'social_pinterest':Configuration.get('SOCIAL_PINTEREST','pinterest.com'),
        'social_youtube':Configuration.get('SOCIAL_YOUTUBE','youtube.com'),
        'footer_categories':HomepageCategory.objects.filter(enabled=True).order_by('priority'),
        'newsletter_subtitle':Configuration.get('NEWSLETTER_SUBTITLE','Subscribe to our newsletter'),
        'primary_categories':Category.objects.filter(parent=None).order_by('priority'),
        'show_popup':Configuration.get('SHOW_POPUP','yes'),
        'popup_return_days':Configuration.get('POPUP_RETURN_NO_OF_DAYS',7),



        #PURCHASE NOTIFIcATION
        # 'purchase_notification_city':random.choice(CityState.objects.all()),
        # 'purchase_notification_product':random.choice(Product.objects.all()),
        # 'purchase_notification_minutes':random.randint(2, 60),
        #random.choice(CityState.objects.all())
        #random.choice(Product.objects.all())

    }
    return kwargs

