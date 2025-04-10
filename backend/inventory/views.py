from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Product, Sale, Category, Shop, AuditLog
from .serializers import ProductSerializer, SaleSerializer, CategorySerializer, ProductViewSerializer, AuditLogSerializer
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from .permissions import IsManager, IsStockClerk, IsSalesPerson
from .utils.audit_logger import log_action
# Create your views here.



# ✅ List all products 
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listProducts(request):
    user = request.user
    shop = get_object_or_404(Shop, owner=user)
    products = Product.objects.filter(shop=shop)
    serializer = ProductViewSerializer(products, many=True)

    log_action(
        request,
        action='VIEW',
        model='Product',
        details={
            'description': f"{user.username} viewed homepage for {shop.name}",
            'shop_id': shop.id,
            'product_count': products.count(),
            'context': 'homepage'
        }
    )

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
        product = serializer.save(shop=shop)

        log_action(
            request,
            action='CREATE',
            user=user,
            model='Product',
            object_id=str(product.id),
            details={
                'description': f"{user.username} added {product.name} for {shop.name}",
                'product_name': product.name,
                'quantity': product.quantity,
                'price': str(product.price),
                'shop': shop.name
            }
        )

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
    user = request.user
    product = get_object_or_404(Product, id=product_id, shop__owner=user)
    
    # Capture old values before updating
    old_data = ProductSerializer(product).data
    
    serializer = ProductSerializer(product, data=request.data)
    if serializer.is_valid():
        serializer.save()

        # Compare old and new values
        new_data = serializer.data
        changes = {k: {'from': old_data[k], 'to': new_data[k]} 
                  for k in old_data if old_data[k] != new_data[k]}

        # Generate a specific description based on changes
        change_descriptions = []
        for field, change in changes.items():
            if field == 'price':
                change_descriptions.append(f"price from GHS {change['from']} to GHS {change['to']}")
            elif field == 'quantity':
                change_descriptions.append(f"quantity from {change['from']} to {change['to']}")
            elif field == 'name':
                change_descriptions.append(f"name from {change['from']} to {change['to']}")
            elif field == 'category':  # Assuming category is an ID or name
                change_descriptions.append(f"category from {change['from']} to {change['to']}")

        
        # Combine changes into a single description
        if change_descriptions:
            description = f"{user.username} updated {', '.join(change_descriptions)} for {product.name}"
        else:
            description = f"{user.username} made no changes to {product.name}"  # Rare case

        log_action(
            request,
            action='UPDATE',
            user=user,
            model='Product',
            object_id=str(product_id),
            details={
                'description': description,
                'product_name': product.name,
                'shop': product.shop.name,
                'changes': changes  # Keep raw changes for reference
            }
        )

        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsManager | IsStockClerk])
def deleteProduct(request, product_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)

    log_action(
        request,
        action='DELETE',
        user=user,
        model='Product',
        object_id=str(product_id),
        details={
            'description': f"{user.username}deleted {product.name} for {product.shop.name}",
            'name': product.name,
            'shop_id': product.shop.id,
            'shop': product.shop.name
        }
    )

    product.delete()
    return Response({"message": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)


# ✅ Record a sale and update stock
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsManager | IsSalesPerson])
def recordSale(request):
    user = request.user
    shop = get_object_or_404(Shop, owner=user)
    sales_data = request.data.get("sales", [])

    if not sales_data:
        return Response({"error": "No sales data provided"}, status=status.HTTP_400_BAD_REQUEST)

    response_data = []
    for sale in sales_data:
        product_id = sale.get("product_id")
        quantity = sale.get("quantity")

        if not product_id or not quantity:
            return Response({"error": "Product ID and quantity are required"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id, shop=shop)
        sale_data = {
            "shop": shop.id,
            "product": product_id,
            "quantity_sold": quantity,
            "total_price": Decimal(quantity) * product.price
        }

        serializer = SaleSerializer(data=sale_data)
        if serializer.is_valid():
            sale_instance = serializer.save()

            log_action(
                request,
                action='SALE',
                user=user,
                model='Sale',
                object_id=str(sale_instance.id),
                details={
                    'description': f"{user.username} sold {quantity} of {product.name} for {shop.name}",
                    'product_name': product.name,
                    'quantity': quantity,
                    'total_price': str(sale_instance.total_price),
                    'shop': shop.name
                }
            )

            response_data.append(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        group_name = user.groups.first().name if user.groups.exists() else None

        try:
            shop = Shop.objects.get(owner=user)
            shop_name = shop.name
        except Shop.DoesNotExist:
            shop_name = None

        log_action(
            request,
            action='LOGIN',
            user=user,  # Explicitly pass the authenticated user
            details={
                'description': f"User '{username}' logged in",  # Add description
                'username': username,
                'shop_name': shop_name,
                'role': group_name
            }
        )

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
    log_action(
        request,
        action='LOGOUT',
        details={'username': request.user.username}
    )
    request.user.auth_token.delete()
    return Response({"message": "Logged out successfully"})
    

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
    




@api_view(["GET"])
@permission_classes([IsAuthenticated, IsManager])  # Restrict to managers only
def auditLogList(request):
    # Fetch all logs, ordered by timestamp (most recent first)
    logs = AuditLog.objects.all().order_by('-timestamp')
    
    serializer = AuditLogSerializer(logs, many=True)
    return Response(serializer.data)