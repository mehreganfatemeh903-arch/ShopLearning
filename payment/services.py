
from abc import abstractmethod, ABC

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings

import requests
import json

from payment.models import Transaction
from store.models import Invoice, Product
from payment.models import Cart


def decrease_stock_product(product, count):
    with transaction.atomic():
        product = Product.objects.select_for_update().get(id=product.id)

        if product.stock < count:
            raise ValueError("Not Enough Stock Available")

        product.stock -= int(count)
        product.save(update_fields=['stock'])


def decrease_stock_from_order(order):
    for order_item in order.detail.all():
        product = order_item.product
        quantity = order_item.quantity
        decrease_stock_product(product, quantity)


def get_payment_service(identifier):
    if identifier == 'paypal':
        return PaypalGateway()

    elif identifier == 'zarinpal':
        return ZarinpalPayment()

    elif identifier == 'google':
        return GooglePayment()

    elif identifier == 'strip':
        return StripPayment()

    elif identifier == 'crypto':
        return CryptoPayment()

    elif identifier == 'mellat':
        return MellatPayment()

    else:
        raise ValueError('Unknown payment')


class BasePaymentGateway(ABC):

    @abstractmethod
    def initiate_payment(self, amount, transaction_code, return_url):
        raise NotImplementedError

    @abstractmethod
    def verify_payment(self, authority, amount, transaction_code):
        raise NotImplementedError

    @abstractmethod
    def payment_success(self, authority, amount, transaction_code, gateway_response):
        raise NotImplementedError

    @abstractmethod
    def payment_fail(self, authority, amount, transaction_code, gateway_response):
        raise NotImplementedError


class PaypalGateway(BasePaymentGateway):

    def initiate_payment(self, amount, transaction_code, return_url):
        pass

    def verify_payment(self, authority, amount, transaction_code):
        pass

    def payment_success(self, authority, amount, transaction_code, gateway_response):
        pass

    def payment_fail(self, authority, amount, transaction_code, gateway_response):
        pass


class CryptoPayment(BasePaymentGateway):

    def initiate_payment(self, amount, transaction_code, return_url):
        pass

    def verify_payment(self, authority, amount, transaction_code):
        pass

    def payment_success(self, authority, amount, transaction_code, gateway_response):
        pass

    def payment_fail(self, authority, amount, transaction_code, gateway_response):
        pass


class GooglePayment(BasePaymentGateway):

    def initiate_payment(self, amount, transaction_code, return_url):
        pass

    def verify_payment(self, authority, amount, transaction_code):
        pass

    def payment_success(self, authority, amount, transaction_code, gateway_response):
        pass

    def payment_fail(self, authority, amount, transaction_code, gateway_response):
        pass


class StripPayment(BasePaymentGateway):

    def initiate_payment(self, amount, transaction_code, return_url):
        pass

    def verify_payment(self, authority, amount, transaction_code):
        pass

    def payment_success(self, authority, amount, transaction_code, gateway_response):
        pass

    def payment_fail(self, authority, amount, transaction_code, gateway_response):
        pass


class ZarinpalPayment(BasePaymentGateway):

    def payment_fail(self, authority, amount, transaction_code, gateway_response):
        pay_fail_general(authority, amount, transaction_code, gateway_response)

    def payment_success(self, authority, amount, transaction_code, gateway_response):
        pay_success_general(amount, transaction_code, gateway_response)

    def initiate_payment(self, amount, transaction_code, return_url, **kwargs):

        if settings.SANDBOX:
            sandbox = 'sandbox.'
        else:
            sandbox = 'payment.'

        ZP_API_REQUEST = f"https://{sandbox}zarinpal.com/pg/v4/payment/request.json"
        ZP_API_STARTPAY = f"https://{sandbox}zarinpal.com/pg/StartPay/"

        data = {
            "merchant_id": settings.MERCHANT,
            "amount": amount,
            "description": "Payment",
            "mobile": "09129999999",
            "callback_url": return_url,
        }

        data = json.dumps(data)

        headers = {
            "content-type": "application/json",
            "content-length": str(len(data))
        }

        try:

            response = requests.post(
                ZP_API_REQUEST,
                data=data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:

                response = response.json()

                if response['data']['code'] == 100:

                    authority = response['data']['authority']

                    return redirect(
                        ZP_API_STARTPAY + authority
                    )

                else:

                    return JsonResponse({
                        "status": False,
                        "code": response['data']['code']
                    })

            return JsonResponse({
                "status": False,
                "message": "Request failed"
            })

        except requests.exceptions.Timeout:

            return JsonResponse({
                "status": False,
                "code": "timeout"
            })

        except requests.exceptions.ConnectionError:

            return JsonResponse({
                "status": False,
                "code": "connection_error"
            })

        except Exception as e:

            return JsonResponse({
                "status": False,
                "error": str(e)
            })

    def verify_payment(self, authority, amount, transaction_code):

        if settings.SANDBOX:
            sandbox = 'sandbox.'
        else:
            sandbox = 'payment.'

        ZP_API_VERIFY = f'https://{sandbox}zarinpal.com/pg/v4/payment/verify.json'

        data = {
            'merchant_id': settings.MERCHANT,
            'amount': amount,
            'authority': authority
        }

        data = json.dumps(data)

        headers = {
            'content-type': 'application/json',
            'content-length': str(len(data)),
            'accept': 'application/json'
        }

        try:

            response = requests.post(
                ZP_API_VERIFY,
                data=data,
                headers=headers,
                timeout=10
            )

            result = response.json()

            if result['data']['code'] in [100, 101]:
                return True, result

            return False, result

        except Exception as e:

            return False, {'error': str(e)}


class MellatPayment(BasePaymentGateway):
    def initiate_payment(self, amount, transaction_code, return_url):
        pass  # بعداً پیاده‌سازی میکنی

    def verify_payment(self, authority, amount, transaction_code):
        return True, {}

    def payment_success(self, authority, amount, transaction_code, gateway_response):
        pass

    def payment_fail(self, authority, amount, transaction_code, gateway_response):
        pass


# -------------------------------------- PAYMENT UPDATE -----------


def pay_success_general(amount, transaction_code, gateway_response):

    transaction_obj = Transaction.objects.get(
        transaction_code=transaction_code,
        amount=amount
    )

    transaction_obj.status = 'complete'
    transaction_obj.response_date = gateway_response
    transaction_obj.save()

    invoice = transaction_obj.invoice
    order = invoice.order

    code = gateway_response['data']['code']

    if code and code == 100:

        try:
            decrease_stock_from_order(order)

            invoice.status = 'paid'
            invoice.save()

            order.status = 1
            order.is_paid = True
            order.save()

            cart = Cart.objects.filter(user=order.customer.user).first()
            if cart:
                cart.items.all().delete()
                cart.has_applied_coupon = False
                cart.save()

        except ValueError:
            invoice.status = 'fail'
            invoice.save()

            order.status = -3
            order.is_paid = False
            order.save()

    else:
        invoice.status = 'fail'
        invoice.save()

        order.status = -2
        order.is_paid = False
        order.save()


def pay_fail_general(authority, amount, transaction_code, gateway_response):
    transaction_obj = Transaction.objects.get(
        transaction_code=transaction_code,
        amount=amount
    )

    transaction_obj.status = 'failed'
    transaction_obj.response_date = gateway_response
    transaction_obj.save()

    invoice = transaction_obj.invoice
    invoice.status = 'fail'
    invoice.save()

    order = invoice.order
    order.status = -2
    order.is_paid = False
    order.save()


