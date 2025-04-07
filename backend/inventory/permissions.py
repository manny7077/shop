from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()

class IsStockClerk(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Stock Clerk').exists()

class IsSalesPerson(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Sales Person').exists()