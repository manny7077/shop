from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Product, Sale, Category, Shop
from .serializers import ProductSerializer, SaleSerializer, CategorySerializer, ProductViewSerializer
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from .permissions import IsManager, IsStockClerk, IsSalesPerson

# Create your views here.



# ✅ List all products / Add a new product
@api_view(["GET"])
@permission_classes([IsAuthenticated])  
def listProducts(request):
    user = request.user
    shop = get_object_or_404(Shop, owner=user)
    products = Product.objects.filter(shop=shop)
    serializer = ProductViewSerializer(products, many=True)
    return Response(serializer.data)

    


@api_view(["GET"])
@permission_classes([IsAuthenticated])  
def listCategories(request):
    if request.method == "GET":
        products = Category.objects.all()
        serializer = CategorySerializer(products, many=True)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsManager | IsStockClerk])  
def createProduct(request):
    user = request.user
    shop = get_object_or_404(Shop, owner=user)

    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(shop=shop)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(["GET"])
@permission_classes([IsAuthenticated, IsManager | IsStockClerk | IsSalesPerson])  
def productDetail(request, product_id):
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)


    if request.method == "GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    
@api_view(["PUT"])  
@permission_classes([IsAuthenticated, IsManager | IsStockClerk])    
def editProduct(request, product_id):
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)

    if request.method == "PUT":
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsManager | IsStockClerk])  
def deleteProduct(request, product_id):
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)

    if request.method == "DELETE":
        product.delete()
        return Response({"message": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)


# ✅ Record a sale and update stock
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsManager | IsSalesPerson])
def recordSale(request):
    # Fetch the logged-in user's shop
    shop = get_object_or_404(Shop, owner=request.user)
    sales_data = request.data.get("sales", [])  # The sale items sent from frontend

    if not sales_data:
        return Response({"error": "No sales data provided"}, status=status.HTTP_400_BAD_REQUEST)

    response_data = []
    for sale in sales_data:
        product_id = sale.get("product_id")  
        quantity = sale.get("quantity")  

        if not product_id or not quantity:
            return Response({"error": "Product ID and quantity are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the product linked to the sale
            product = get_object_or_404(Product, id=product_id, shop=shop)
            
            # Prepare sale data including the shop field
            sale_data = {
                "shop": shop.id,  # Explicitly include the shop ID here
                "product": product_id,
                "quantity_sold": quantity,
                "total_price": Decimal(quantity) * product.price
            }

            # Serialize and save the sale record
            serializer = SaleSerializer(data=sale_data)
            if serializer.is_valid():
                serializer.save()
                response_data.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(response_data, status=status.HTTP_201_CREATED)



@api_view(['GET'])
def salesCount(request):
    shop = get_object_or_404(Shop, owner=request.user)
    today = now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    daily_sales = Sale.objects.filter(
        created_at__date=today,
        product__shop=shop
    ).aggregate(total=Sum('total_price'))['total'] or 0

    weekly_sales = Sale.objects.filter(
        created_at__date__gte=week_start,
        product__shop=shop
    ).aggregate(total=Sum('total_price'))['total'] or 0

    monthly_sales = Sale.objects.filter(
        created_at__date__gte=month_start,
        product__shop=shop
    ).aggregate(total=Sum('total_price'))['total'] or 0

    return Response({
        "daily_sales": daily_sales,
        "weekly_sales": weekly_sales,
        "monthly_sales": monthly_sales
    })




@api_view(["POST"])
def loginView(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=400)

    user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        group_name = None
        if user.groups.exists():
            # Get the first group name (assuming users belong to only one group)
            group_name = user.groups.first().name

        try:
            shop = Shop.objects.get(owner=user)
            shop_name = shop.name
        except Shop.DoesNotExist:
            shop_name = None

        return Response({
            "token": token.key,
            "message": "Login successful",
            "shop_name": shop_name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": group_name
        })
    else:
        return Response({"error": "Invalid credentials"}, status=401)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logoutView(request):
    """Logout user by deleting the token"""
    try:
        # Delete the token associated with the current user
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"})
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getShopInfo(request):
    try:
        # Get the shop associated with the logged-in user
        shop = get_object_or_404(Shop, owner=request.user)
        
        # Return the shop ID and name
        return Response({
            "shop_id": shop.id,
            "shop_name": shop.name
        })
    except Shop.DoesNotExist:
        return Response({"error": "No shop found for the logged-in user"}, status=404)