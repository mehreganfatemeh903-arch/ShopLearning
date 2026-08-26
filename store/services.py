from itertools import count

from django.utils import timezone
from payment.models import Transaction
from django.db import transaction
import requests
from django.urls import reverse

from payment.services import get_payment_service
from store.models import Invoice, OrderItem, Product, Customer, Order
from store.signals import generate_unique_invoice_number, generate_unique_transaction_number
from django.shortcuts import get_object_or_404

def create_invoices_pending(instance):
    invoice = Invoice.objects.create(
        invoice_number=generate_unique_invoice_number(instance.id),
        order=instance,
        amount=instance.total_price,
        status='pending',
        expired_at=timezone.now() + timezone.timedelta(hours=24)
    )
    return invoice

def create_transactions_pending(invoice, order_model):
    transaction = Transaction.objects.create(
        invoice=invoice,
        amount=invoice.amount,
        status='pending',
        transaction_code=generate_unique_transaction_number(invoice.id),
        payment_method=order_model.payment_method,
    )
    return transaction


def create_order_item_form_cart(cart_model,order_model):
    for item in cart_model.items.all():
        OrderItem.objects.create(
            order=order_model,
            product=item.product,
            quantity=item.quantity,
            price=item.price_item
        )




def check_stock(product,quantity) :
    if product.stock -int(quantity)>=0:
        return True
    else:
        return False



def increase_stock_product(product, count):
    product.stock += int(count)
    product.save()


def cart_items_is_empty(cart_model):
    if cart_model.items.count() == 0:
        raise ValueError('No items found')


#
# def init_checkout_cart(form,cart_model):
#     cart_items_is_empty(cart_model)
#     order_model = form.save(commit=False)
#     total_price = sum(item.get_total_price_item() for item in cart_model.items.all())
#     order_model.total_price = total_price
#     order_model.save()
#     create_order_item_form_cart(cart_model, order_model)
#     invoice = create_invoices_pending(order_model)
#     transaction_code = create_transactions_pending(invoice, order_model)
#
#     # cart_model.delete()
#     return order_model , invoice,transaction_code,



def init_checkout_cart(form, cart_model):
    cart_items_is_empty(cart_model)

    customer = Customer.objects.get(user=cart_model.user)

    total_price = sum(item.get_total_price_item() for item in cart_model.items.all())

    # ساخت سفارش به صورت کامل
    order_model = Order.objects.create(
        customer=customer,
        total_price=total_price,
        address_line=form.cleaned_data['address_line'],
        city=form.cleaned_data['city'],
        payment_method=form.cleaned_data['payment_method'],
        shipping_method=form.cleaned_data['shipping_method'],
        note=form.cleaned_data.get('note', ''),
        status=0,  # Pending
        method_out=True
    )

    # ساخت آیتم‌های سفارش
    create_order_item_form_cart(cart_model, order_model)

    # ساخت فاکتور
    invoice = create_invoices_pending(order_model)

    # ساخت تراکنش
    transaction_code = create_transactions_pending(invoice, order_model)

    return order_model, invoice, transaction_code





def init_checkout_pyment_cart(request,order_model,transaction_model):
    payment_method_identifier = order_model.payment_method.identifier
    gateway = get_payment_service(payment_method_identifier)
    callback_url = request.build_absolute_uri(
        reverse('payment_callback', args=[transaction_model.transaction_code]))

    redirect_url = gateway.initiate_payment(
        amount=transaction_model.amount,
        transaction_code=transaction_model.transaction_code,
        return_url=callback_url
    )
    return redirect_url





