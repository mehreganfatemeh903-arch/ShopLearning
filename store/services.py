from django.utils import timezone
from django.db import transaction
from django.urls import reverse

from payment.models import Transaction
from payment.services import get_payment_service

from store.models import (
    Invoice,
    OrderItem,
    Product,
    Customer,
    Order,
)

from store.signals import (
    generate_unique_invoice_number,
    generate_unique_transaction_number,
)


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


def create_order_item_form_cart(cart_model, order_model):
    for item in cart_model.items.all():
        OrderItem.objects.create(
            order=order_model,
            product=item.product,
            quantity=item.quantity,
            price=item.price_item
        )


def check_stock(product, quantity):
    """
    بررسی می‌کند که موجودی محصول برای تعداد درخواستی کافی باشد.
    """
    try:
        requested_quantity = int(quantity)
        current_stock = int(product.stock or 0)
    except (TypeError, ValueError):
        return False

    return current_stock >= requested_quantity


def increase_stock_product(product, count):
    """
    افزایش موجودی محصول.
    """
    product.stock = int(product.stock or 0) + int(count)
    product.save(update_fields=['stock'])


def cart_items_is_empty(cart_model):
    """
    بررسی خالی نبودن سبد خرید.
    """
    if cart_model.items.count() == 0:
        raise ValueError('No items found')


def init_checkout_cart(form, cart_model):
    """
    ایجاد سفارش، آیتم‌های سفارش، فاکتور و تراکنش.

    نکته مهم:
    قبل از ساخت سفارش، موجودی تمام کالاهای سبد خرید بررسی می‌شود.
    اگر حتی یک کالا موجودی کافی نداشته باشد،
    هیچ سفارش یا تراکنشی ایجاد نمی‌شود و ValueError برمی‌گردد.
    """

    # -----------------------------------------
    # 1. بررسی خالی نبودن سبد خرید
    # -----------------------------------------
    cart_items_is_empty(cart_model)

    # -----------------------------------------
    # 2. بررسی موجودی تمام کالاها
    # -----------------------------------------
    for item in cart_model.items.all():

        if not check_stock(
            item.product,
            item.quantity
        ):
            raise ValueError(
                f"Not Enough Stock Available: {item.product.name}"
            )

    # -----------------------------------------
    # 3. پیدا کردن مشتری
    # -----------------------------------------
    customer = Customer.objects.get(
        user=cart_model.user
    )

    # -----------------------------------------
    # 4. محاسبه مبلغ کل
    # -----------------------------------------
    total_price = sum(
        item.get_total_price_item()
        for item in cart_model.items.all()
    )

    # -----------------------------------------
    # 5. ساخت سفارش
    # -----------------------------------------
    order_model = Order.objects.create(
        customer=customer,
        total_price=total_price,
        address_line=form.cleaned_data['address_line'],
        city=form.cleaned_data['city'],
        payment_method=form.cleaned_data['payment_method'],
        shipping_method=form.cleaned_data['shipping_method'],
        note=form.cleaned_data.get('note', ''),
        status=0,
        method_out=True
    )

    # -----------------------------------------
    # 6. ساخت آیتم‌های سفارش
    # -----------------------------------------
    create_order_item_form_cart(
        cart_model,
        order_model
    )

    # -----------------------------------------
    # 7. ساخت فاکتور
    # -----------------------------------------
    invoice = create_invoices_pending(
        order_model
    )

    # -----------------------------------------
    # 8. ساخت تراکنش
    # -----------------------------------------
    transaction_model = create_transactions_pending(
        invoice,
        order_model
    )

    # -----------------------------------------
    # 9. برگرداندن اطلاعات
    # -----------------------------------------
    return (
        order_model,
        invoice,
        transaction_model
    )


def init_checkout_pyment_cart(
    request,
    order_model,
    transaction_model
):
    """
    ارسال تراکنش به درگاه پرداخت.
    """

    payment_method_identifier = (
        order_model.payment_method.identifier
    )

    gateway = get_payment_service(
        payment_method_identifier
    )

    callback_url = request.build_absolute_uri(
        reverse(
            'payment_callback',
            args=[
                transaction_model.transaction_code
            ]
        )
    )

    redirect_url = gateway.initiate_payment(
        amount=transaction_model.amount,
        transaction_code=transaction_model.transaction_code,
        return_url=callback_url
    )

    return redirect_url