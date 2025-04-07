from django.urls import path
from . import views

urlpatterns = [
    # ✅ Product URLs
    path("products/", views.listProducts),
    path("products/add/", views.createProduct),
    path("products/<int:product_id>/", views.productDetail),
    path("products/edit/<int:product_id>/", views.editProduct),
    path("products/delete/<int:product_id>/", views.deleteProduct),

    # ✅ Sales URL
    path("sales/record/", views.recordSale),
    path('sales/counts/', views.salesCount),
    path("categories/", views.listCategories),


    path("login/", views.loginView),
    path("logout/", views.logoutView),
    path("shop/info/", views.getShopInfo),
]