from django.contrib import admin
from .models import Product, HealthTip, ProductCategory, \
    HealthTipCategory


# Register your models here.
admin.site.register(Product)
admin.site.register(HealthTip)
admin.site.register(ProductCategory)
admin.site.register(HealthTipCategory)