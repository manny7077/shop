from django.contrib import admin
from .models import Product, Sale, Category, StockAlert
# Register your models here.


admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(Category)
admin.site.register(StockAlert)