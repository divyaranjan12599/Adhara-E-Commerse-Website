import csv
from shop.models import *
from core import choices
from datetime import datetime
import time
import json
import re
from django.db import models
from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from core.utils import compress
from django.conf import settings
with open('scripts/data.csv') as csvfile:
    spamreader = csv.reader(csvfile)
    counter =0
    color_attr,created = Attribute.objects.get_or_create(name="Color")
    size_attr,created = Attribute.objects.get_or_create(name="Size")
        
    for row in spamreader:
        counter += 1
        print(counter)
        print(row)
        if counter == 1:
            continue
        d={}
        d['option_sku']=row[0]
        d['mrp']=int(row[1])
        d['selling_price']=int(row[2])
        d['transfer_price']=int(row[3])
        d['category_name']=row[4].title()
        d['name']=row[5].title()
        d['description']=row[6]
        d['feature']=row[7]
        d['hsn']=row[8]
        d['img1']=row[9]
        d['img2']=row[10]
        d['img3']=row[11]
        d['img4']=row[12]
        d['img5']=row[13]
        d['img6']=row[14]
        d['sku']= row[15]
        d['total_without_tax']=int(float(row[17]))
        d['discount']=int(float(row[20]))
        #create category
        category,created=Category.objects.get_or_create(name=d.get('category_name'))
        tax_class,created=TaxClass.objects.get_or_create(name='Apparel and Clothing')
        #create product
        print("d.get('sku')",d.get('sku'))
        p,created=Product.objects.get_or_create(sku=d.get('sku'))
        p.name=d.get('name')
        p.manufacturer_id=1
        p.summary=d.get('feature')
        p.primary_category=category
        p.primary_attribute=color_attr
        p.description=d.get('description')
        p.hsn=d.get('hsn')
        p.tax_class=tax_class
        p.save()
        #create product option
        print("d.get('transfer_price')",d.get('transfer_price'))
        print(d)
        po_sku_without_size=d.get('option_sku')
        po = ProductOption.objects.filter(sku__startswith=po_sku_without_size).last()
        if po is None:
            po,created=ProductOption.objects.get_or_create(product=p,sku=d.get('option_sku'),min_sp=d.get('transfer_price'))
        po.quantity=100
        po.rate=d.get('total_without_tax')
        po.discount_percentage=d.get('discount')
        po.min_sp=d.get('transfer_price')
        po.save()
        # color_sizes = d.get('option_sku').replace(d.get('sku')).rsplit('_',1)
        color=row[21]
        size=row[22]
        ProductOptionAttributes.objects.get_or_create(product_option=po,attribute=color_attr,value=color,label=color)
        ProductOptionAttributes.objects.get_or_create(product_option=po,attribute=size_attr,value=size,label=size)
        #if the same color option already exists, we assume images are already uploaded for that
        if ProductOptionImage.objects.filter(product_option__product=po.product,\
            product_option__attributes__attribute=color_attr,\
            product_option__attributes__value=color).count() ==0:
            ProductOptionImage.objects.filter(product_option=po).delete()
            for k,v in d.items():
                if 'img' in k and v:
                    v=v.replace('dl=0','dl=1')
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(urlopen(v).read())
                    img_temp.flush()
                    img_temp.name="{}.jpg".format(po.id)
                    poi=ProductOptionImage.objects.create(product_option=po,image=File(img_temp),priority=k.replace('img',''))
                    if settings.DEBUG:
                        poi.image=compress(poi.image)
                        poi.save()
                    # image_file.save(f"image_{self.pk}", File(img_temp)