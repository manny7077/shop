from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Product, Sale, Category
from .serializers import ProductSerializer, SaleSerializer, CategorySerializer, ProductViewSerializer
from django.db.models import Sum
from django.utils.timezone import now, timedelta

# Create your views here.



# ✅ List all products / Add a new product
@api_view(["GET"])
def listProducts(request):
    if request.method == "GET":
        products = Product.objects.all()
        serializer = ProductViewSerializer(products, many=True)
        return Response(serializer.data)
    


@api_view(["GET"])
def listCategories(request):
    if request.method == "GET":
        products = Category.objects.all()
        serializer = CategorySerializer(products, many=True)
        return Response(serializer.data)


@api_view(["POST"])
def createProduct(request):
    if request.method == "POST":
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
def productDetail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    
@api_view(["PUT"])    
def editProduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "PUT":
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def deleteProduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "DELETE":
        product.delete()
        return Response({"message": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)


# ✅ Record a sale and update stock
@api_view(["POST"])
def recordSale(request):
    sales_data = request.data.get("sales", [])  

    if not sales_data:
        return Response({"error": "No sales data provided"}, status=status.HTTP_400_BAD_REQUEST)

    response_data = []
    for sale in sales_data:
        product_id = sale.get("product_id")  
        quantity = sale.get("quantity")  

        if not product_id or not quantity:
            return Response({"error": "Product ID and quantity are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = get_object_or_404(Product, id=product_id)
            
            sale_data = {
                "product": product_id,
                "quantity_sold": quantity,
                "total_price": quantity * product.price,
            }

            serializer = SaleSerializer(data=sale_data)
            if serializer.is_valid():
                serializer.save()  # Stock will be deducted automatically in the model's save method
                response_data.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(response_data, status=status.HTTP_201_CREATED)















@api_view(['GET'])
def salesCount(request):
    today = now().date()
    week_start = today - timedelta(days=today.weekday())  # Start of the current week
    month_start = today.replace(day=1)  # Start of the month

    daily_sales = Sale.objects.filter(created_at__date=today).aggregate(total=Sum('total_price'))['total'] or 0
    weekly_sales = Sale.objects.filter(created_at__date__gte=week_start).aggregate(total=Sum('total_price'))['total'] or 0
    monthly_sales = Sale.objects.filter(created_at__date__gte=month_start).aggregate(total=Sum('total_price'))['total'] or 0

    return Response({
        "daily_sales": daily_sales,
        "weekly_sales": weekly_sales,
        "monthly_sales": monthly_sales
    })