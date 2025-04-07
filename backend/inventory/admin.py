from django.contrib import admin
from .models import Product, Sale, Category, StockAlert, Shop
# Register your models here.


admin.site.register(Product)
admin.site.register(Sale)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(StockAlert)
admin.site.register(Shop)