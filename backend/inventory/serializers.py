from rest_framework import serializers
from .models import Product, Sale, Category, AuditLog

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class ProductViewSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    shop_name = serializers.CharField(source="shop.name", read_only=True)


    class Meta:
        model = Product
        fields = "__all__"



class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = "__all__"


class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField() 
    action_display = serializers.CharField(source='get_action_display')  # Human-readable action

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'action_display', 'model', 'object_id', 'details', 'ip_address', 'timestamp']


