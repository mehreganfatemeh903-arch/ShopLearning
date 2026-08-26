from django.contrib import admin
from payment.models import PaymentMethod, ShippingMethod, Cart, CartItem


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_per_page = 4


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_per_page = 4


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'Session_key', 'has_applied_coupon')
    list_per_page = 10


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    list_per_page = 10