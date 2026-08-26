from django.db import models
from django.db.models import SET_NULL
from typing import Any


from users.models import PersonUser

# Create your models here.



class Cart(models.Model):
    user=models.ForeignKey(PersonUser,on_delete=models.CASCADE,null=True,blank=True)

    Session_key=models.CharField(max_length=40,null=True,blank=True)

    create_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    has_applied_coupon=models.BooleanField(default=False)

    def __str__(self):
        return f"Cart {self.id} - User:{self.user} - Session:{self.Session_key}"






    def get_total_price_cart(self):
        return sum(item.get_total_price_item() for item in self.items.all())



class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey('store.Product',on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)
    price_item=models.FloatField(default=0)
    added_at=models.DateTimeField(auto_now_add=True)

    def get_total_price_item(self):
        return self.price_item*self.quantity




# درست:
# class OrderItem(models.Model):
#     order = models.ForeignKey('store.Order', on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey('store.Product', on_delete=models.CASCADE, related_name='order_items')
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return f"{self.quantity} * {self.product.name}"




class PaymentMethod(models.Model):
    name=models.CharField(max_length=50) #bitcoin,strip,zarinpal,paypal
    identifier=models.SlugField(unique=True)
    active=models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ShippingMethod(models.Model):
    name=models.CharField(max_length=100)
    cost=models.FloatField(default=0)
    estimate_day=models.PositiveIntegerField(null=True,blank=True)
    active=models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    invoice = models.ForeignKey(
        'store.Invoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='Transaction'
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True
    )
    amount = models.FloatField()
    transaction_code = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=30, choices=[
        ('pending', 'Pending'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ])
    create_at = models.DateTimeField(auto_now_add=True)
    response_date = models.JSONField(null=True, blank=True)