from ecommerce.celery import app
import csv
from shop.models import Manufacturer,CityState,Attribute,Category,Product,ProductAttributes,ProductOption,ProductOptionImage,ProductOptionAttributes, TaxClass
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from core import choices

class ProductUploadingViaCsv(object):    
    def create_manufacturer(self,row):
        # Manufacture Model Object Create
        manufacturer_object,manufacturer_ = Manufacturer.objects.get_or_create(name=row.get("Brand"))
        return manufacturer_object
    
    def create_citystate(self,row):
        #CityState Object
        location_object,location_ = CityState.objects.get_or_create(name="Jaipur",type=choices.CityStateType.CITY)
        return location_object
    
    def create_attribute(self,row):
        # Attribute Object create
        primary_attribute_object,primary_attribute_ = Attribute.objects.get_or_create(name="Color")
        return primary_attribute_object
        
    def create_product(self,row,category_choice):
        
        #create manufacturer Object
        manufacturer_object=self.create_manufacturer(row)
        
        # Category Model Object
        category_object=Category.objects.get(id=category_choice)
        
        #CityState Object
        location_object = self.create_citystate(row)
        
        # Attribute Object create
        primary_attribute_object = self.create_attribute(row)

        # Product Object create
        product,_ = Product.objects.get_or_create(sku=row.get("Group ID"))
        product.name=row.get("Product Name")
        if row.get("Summary") !="":
            product.summary=row.get("Summary")
        product.description=row.get("Description")
        product.manufacturer=manufacturer_object
        product.primary_category=category_object
        product.categories.add(category_object)
        product.hsn=row.get("HSN")
        product.location=location_object
        product.tax_class = TaxClass.objects.first()
        product.status=choices.StatusChoices.ENABLED if str(row.get("Status")).lower() == "active" else choices.StatusChoices.DISABLED

        if row.get("Return Days") != "":
            product.return_days=int(row.get("Return Days"))
        else:
            product.return_days=15
            
        if row.get("Youtube Link") != "":
            product.youtube_link=row.get("Youtube Link")
        product.weight_gram=int(row.get("Weight  (GM)"))
        
        product.primary_attribute=primary_attribute_object
        
        if row.get("Width") != "":
            product.width=row.get("Width")
        if row.get("Height") !="":
            product.height=row.get("Height")
        if row.get("Length") != "":
            product.length=row.get("Length")
       
        product.save()
        
        return product
    
    def create_product_attribute(self,row,product):
        try:
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Style Code",value=row.get("Style Code"))
            product_attr.save()
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Shape Type",value=row.get("Shape Type"))
            product_attr.save()  
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Length Type",value=row.get("Length Type"))
            product_attr.save()  
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Pattern",value=row.get("Pattern"))
            product_attr.save() 
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Occasion",value=row.get("Occasion"))
            product_attr.save() 
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Fabric",value=row.get("Fabric"))
            product_attr.save() 
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Pack Of",value=row.get("Pack Of"))
            product_attr.save() 
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Neck Type",value=row.get("Neck Type"))
            product_attr.save() 
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Sleeve Length",value=row.get("Sleeve Length"))
            product_attr.save() 
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Sleeve Style",value=row.get("Sleeve Style"))
            product_attr.save() 
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Detail Placement",value=row.get("Detail Placement"))
            product_attr.save() 
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Fabric Purity",value=row.get("Fabric Purity"))
            product_attr.save() 
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Country Of Origin",value=row.get("Country Of Origin"))
            product_attr.save() 
            product_attr,_=ProductAttributes.objects.get_or_create(product=product,name="Ornamentation Type",value=row.get("Ornamentation Type"))
            product_attr.save() 
        except:
            pass
    
    def create_productOption(self,row,product):
        product_option,_ = ProductOption.objects.get_or_create(product=product,sku=row.get("Seller SKU"))
        product_option.product = product
        product_option.quantity = row.get("Stock")
        product_option.list_price = row.get("MRP")
        product_option.selling_price = row.get("Selling Price")
        product_option.save()
        return product_option
    
    def create_product_option_attribute(self,row,product_option):
        color_attr=self.create_attribute(row)
        poa,created=ProductOptionAttributes.objects.get_or_create(product_option=product_option,attribute=color_attr,value=row.get("Color"),label=row.get("Color"))
        size_attr,created=Attribute.objects.get_or_create(name="Size")
        poa,created=ProductOptionAttributes.objects.get_or_create(product_option=product_option,attribute=size_attr,value=row.get("Size"))
        poa.label=row.get("Size")
        poa.save()
    
    def save_one_product(self,row,category_choice):
        # create product Opject
        product = self.create_product(row,category_choice)
        #Create Product Attribute
        self.create_product_attribute(row,product)
        # Product Option Create
        product_option=self.create_productOption(row,product)
        #Create ProductOption Attribute
        self.create_product_option_attribute(row,product_option)
        #product Image Uploading
        self.product_image_upload(row,product_option)
        
    def product_image_upload(self,row,product_option):
        ProductOptionImage.objects.filter(product_option=product_option).delete()
        for i in range(1,9):
            if row.get("Image Link {}".format(i)) != "":
                try:
                    image_url=row.get("Image Link {}".format(i))
                    r = requests.get(image_url)
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(r.content)
                    img_temp.flush()
                    poi=ProductOptionImage.objects.create(product_option=product_option)
                    poi.priority=i
                    poi.image.save("produt_{}.jpg".format(poi.id),File(img_temp),save=True)
                except Exception as e:
                    print(e)
        
        
@app.task
def upload_product_data_via_csv(row,category_choice):
    product_csv=ProductUploadingViaCsv()
    product_csv.save_one_product(row,category_choice)


