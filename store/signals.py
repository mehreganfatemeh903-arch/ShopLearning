
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from payment.models import Transaction
from store.models import ProductDiscount, CategoryDiscount, SpecialProduct, Order, Invoice


@receiver(post_save,sender=ProductDiscount)
def update_product_discount_save(sender,instance,created,**kwargs):
    product=instance.product
    product.save()


@receiver(post_save, sender=CategoryDiscount)
def update_category_product_discount_save(sender, instance, created, **kwargs):
    for product in instance.category.products.all():
        product.save()


@receiver(post_delete,sender=CategoryDiscount)
def delete_category_product_discount_delete(sender,instance,**kwargs):
    for product in instance.category.products.all():
        product.save()


@receiver(post_save,sender=SpecialProduct)
def update_special_product_discount_save(sender,instance,created,**kwargs):
    product = instance.product
    product.save()

@receiver(post_delete,sender=SpecialProduct)
def delete_special_product_discount_delete(sender,instance,**kwargs):
    product = instance.product
    product.save()


def generate_unique_invoice_number(order_id):
    now=timezone.now()
    time_now_str=now.strftime("%Y%m%d%H%M%S")
    return f"INVOICE_{order_id}-{time_now_str}"



def generate_unique_transaction_number(invoice_id):
    now = timezone.now()
    time_now_str = now.strftime("%Y%m%d%H%M%S")
    return f"T_{invoice_id}_{time_now_str}"


# @receiver(post_save,sender=Order)
# def create_invoice_order(sender,instance,created,**kwargs):
#     if created:
#         invoice=Invoice.objects.create(
#             invoice_number=generate_unique_invoice_number(instance.id),
#             order=instance,
#             amount=instance.total_price,
#             status='pending',
#             expired_at=timezone.now()+timezone.timedelta(hours=24)
#         )
#
#         Transaction.objects.create(
#            invoice=invoice,
#             amount=invoice.total_price,
#             status='pending',
#             transaction_code=generate_unique_transaction_number(invoice.id),
#             payment_method=invoice.payment_method,
#         )
#         return transaction