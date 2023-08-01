from jinja2 import FileSystemLoader, TemplateNotFound
from os.path import join, exists, getmtime
from django.conf import settings
class MyLoader(FileSystemLoader):
    def __init__(self,path):
        super().__init__(path)
        
    def get_source(self, environment, template):
        if "storefront" in template and settings.STOREFRONT_NAME.lower()=="ragavi":
            template = template.replace("storefront","ragavi_storefront")
        return super(MyLoader, self).get_source(environment, template)
