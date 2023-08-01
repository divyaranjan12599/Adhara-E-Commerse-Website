from django.conf import settings
import math
from django.db.models import F

from io import BytesIO
from PIL import Image
from django.core.files import File
import math

def build_breadcrumb(list_of_dict):
	lst = []
	home={}
	home['title']="Home"
	home['url'] = '/'
	home['text'] = "Home"
	lst.append(home)
	lst.extend(list_of_dict)
	return lst

def build_html_head(**kwargs):
	return kwargs



def price_format(price):
	return "{} {}".format(settings.RUPEE_SYMBOL,price)


def per_cent_amount(rate, percentage, use_ceil=False):
	'''
	Main calculator for rate and discounts
	:param rate:
	:param percentage:
	:param use_ceil: for tax calculations, never avoid tax amount even less than 1 rs
	:return:
	'''
	if use_ceil:
		return int(math.ceil((rate * percentage) / 100.0))
	return int(round((rate * percentage) / 100.0))

def per_cent_tax(rate, percentage, use_ceil=False):
	if use_ceil:
		return int(math.ceil((rate * 100) / (100.0 + percentage)))
	return int(round((rate * 100) / (100.0+percentage)))


def sort_products(products,sortby):
	if sortby:
		if sortby == "a2z":
			return products.order_by('name')
		elif sortby == "z2a":
			return products.order_by('-name')
		elif sortby == "1to10":
			return products.order_by('options__rate').distinct()
			return products.order_by(F('options__rate') - F('options__rate') * F('options__discount_percentage'))
		elif sortby == "10to1":
			return products.order_by('-options__rate').distinct()

			return products.order_by(F('options__rate') - F('options__rate') - F('options__rate') * F('options__discount_percentage'))
	return products

def sort_options(options,sortby):
	if sortby:
		if sortby == "a2z":
			return options.order_by('product__name')
		elif sortby == "z2a":
			return options.order_by('-product__name')
		elif sortby == "1to10":
			return options.order_by('selling_price')
			return options.order_by(F('rate') - F('rate') * F('discount_percentage'))
		elif sortby == "10to1":
			return options.order_by('-selling_price').distinct()
		elif sortby == "recent":
			return options.order_by('-created')
	return options



def compress(image,resize_height=1250):
	im = Image.open(image)

	if resize_height:
		width, height = im.size
		height /=4
		width /= 4 
		# newheight = ratio * 1250

		im=im.resize((int(width), int(height)), Image.ANTIALIAS)
	
	# create a BytesIO object
	im_io = BytesIO() 
	# save image to BytesIO object
	im.save(im_io, 'JPEG', quality=70) 
	# create a django-friendly Files object
	new_image = File(im_io, name=image.name)
	return new_image