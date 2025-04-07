from django.db import models
from django.contrib.auth.models import User

# Create your models here

class Shop(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ManyToManyField(User)

    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")  # NEW
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.quantity} in stock"


class Sale(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="sales")  # NEW
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.product.quantity >= self.quantity_sold:
                self.product.quantity -= self.quantity_sold
                self.product.save()
            else:
                raise ValueError("Not enough stock")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale: {self.quantity_sold} x {self.product.name} on {self.created_at}"



class StockAlert(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    threshold = models.PositiveIntegerField(default=2)  
    is_alerted = models.BooleanField(default=False)  

    def __str__(self):
        return f"Alert for {self.product.name} (Threshold: {self.threshold})"
