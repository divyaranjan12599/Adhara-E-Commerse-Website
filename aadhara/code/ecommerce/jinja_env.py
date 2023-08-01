from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from ecommerce.my_loader import MyLoader
from jinja2 import Environment,FileSystemLoader
from django.conf import settings
from django.utils.safestring import mark_safe
# from django.contrib.staticfiles.templatetags.staticfiles import static
from django.templatetags.static import static
from datetime import datetime
from django.utils.text import slugify


def img_tag(*args,**kwargs):
    src = kwargs['src']
    # print("src",type(src))
    size = kwargs['size']
    width=size.split('/')[0]
    height=size.split('/')[1]
    url_only=False

    url =""
    if settings.DEBUG:
        url = src
    else:
        url = 'https://img.aadhara.in/a/fit/{}/sm/0/plain/local://{}'.format(size,static(src))
        url = 'https://img.aadhara.in/preset:sharp/trim:1/resize:fit:{}:{}:1:1/gravity:sm/plain/local://{}'.format(width,height,static(src))
    if 'url_only' in kwargs and kwargs['url_only']:
        return url

    class_name=kwargs.get('class_name',"")
    alt = kwargs.get('alt','Photo')
    
    full_tag= "<img alt='{}' src='{}' class='{}' width='{}px' height='{}px' style='width:{}px;' >".format(alt,url,class_name,width,height,width)
    return mark_safe(full_tag)


one = ["", "one ", "two ", "three ", "four ",
       "five ", "six ", "seven ", "eight ",
       "nine ", "ten ", "eleven ", "twelve ",
       "thirteen ", "fourteen ", "fifteen ",
       "sixteen ", "seventeen ", "eighteen ",
       "nineteen "];

# strings at index 0 and 1 are not used,
# they is to make array indexing simple
ten = ["", "", "twenty ", "thirty ", "forty ",
       "fifty ", "sixty ", "seventy ", "eighty ",
       "ninety "];
# n is 1- or 2-digit number
def numToWords(n, s):
    str = "";

    # if n is more than 19, divide it
    if (n > 19):
        str += ten[n // 10] + one[n % 10];
    else:
        str += one[n];

        # if n is non-zero
    if (n):
        str += s;

    return str;

def slug(value):
    return slugify(value)

def date_format(date_obj):
    return date_obj.strftime('%b %d, %Y')

def convertToWords(n):
    # stores word representation of given
    # number n
    import math
    n = math.floor(n)
    out = "";

    # handles digits at ten millions and
    # hundred millions places (if any)
    out += numToWords((n // 10000000),
                      "crore ");

    # handles digits at hundred thousands
    # and one millions places (if any)
    out += numToWords(((n // 100000) % 100),
                      "lakh ");

    # handles digits at thousands and tens
    # thousands places (if any)
    out += numToWords(((n // 1000) % 100),
                      "thousand ");

    # handles digit at hundreds places (if any)
    out += numToWords(((n // 100) % 10),
                      "hundred ");

    if (n > 100 and n % 100):
        out += "and ";

        # handles digits at ones and tens
    # places (if any)
    out += numToWords((n % 100), "");

    return out;


def price_format(price):
    return "{} {}".format(settings.RUPEE_SYMBOL,price)

def mega_menu():
    from shop.models import Category
    return Category.objects.filter(parent__isnull=True).order_by('priority')

def environment(**options):
    options['loader']= MyLoader("templates")
    env = Environment(cache_size=0,**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'img_tag':img_tag,
        'MEDIA_URL': settings.MEDIA_URL,
        'now':datetime.now(),
        'DEBUG':settings.DEBUG,
        'price_format':price_format,
        'convert_to_words':convertToWords,
        'menu_categories':mega_menu,
        'slug':slug,
        'date_format':date_format,
        'Year':datetime.now().year            #pass copyright year dynamically
            
    })
    return env



    

