from abc import abstractmethod, ABC

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings

import requests
import json

from payment.models import Transaction, Cart
from store.models import Invoice, Product


def decrease_stock_product(product, count):
    with transaction.atomic():
        product = Product.objects.select_for_update().get(id=product.id)

        if product.stock < count:
            raise ValueError(
                f"Not Enough Stock Available: {product.name}"
            )

        product.stock -= int(count)
        product.save(update_fields=["stock"])


def decrease_stock_from_order(order):
    for order_item in order.detail.select_related("product").all():
        product = order_item.product
        quantity = order_item.quantity
        decrease_stock_product(product, quantity)


def get_payment_service(identifier):
    if identifier == "paypal":
        return PaypalGateway()

    elif identifier == "zarinpal":
        return ZarinpalPayment()

    elif identifier == "google":
        return GooglePayment()

    elif identifier == "strip":
        return StripPayment()

    elif identifier == "crypto":
        return CryptoPayment()

    elif identifier == "mellat":
        return MellatPayment()

    else:
        raise ValueError("Unknown payment")


class BasePaymentGateway(ABC):

    @abstractmethod
    def initiate_payment(self, amount, transaction_code, return_url):
        raise NotImplementedError

    @abstractmethod
    def verify_payment(self, authority, amount, transaction_code):
        raise NotImplementedError

    @abstractmethod
    def payment_success(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        raise NotImplementedError

    @abstractmethod
    def payment_fail(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        raise NotImplementedError


class PaypalGateway(BasePaymentGateway):

    def initiate_payment(self, amount, transaction_code, return_url):
        pass

    def verify_payment(self, authority, amount, transaction_code):
        pass

    def payment_success(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pass

    def payment_fail(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pass


class CryptoPayment(BasePaymentGateway):

    def initiate_payment(self, amount, transaction_code, return_url):
        pass

    def verify_payment(self, authority, amount, transaction_code):
        pass

    def payment_success(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pass

    def payment_fail(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pass


class GooglePayment(BasePaymentGateway):

    def initiate_payment(self, amount, transaction_code, return_url):
        pass

    def verify_payment(self, authority, amount, transaction_code):
        pass

    def payment_success(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pass

    def payment_fail(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pass


class StripPayment(BasePaymentGateway):

    def initiate_payment(self, amount, transaction_code, return_url):
        pass

    def verify_payment(self, authority, amount, transaction_code):
        pass

    def payment_success(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pass

    def payment_fail(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pass


class ZarinpalPayment(BasePaymentGateway):

    def payment_fail(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pay_fail_general(
            authority,
            amount,
            transaction_code,
            gateway_response
        )

    def payment_success(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pay_success_general(
            amount,
            transaction_code,
            gateway_response
        )

    def initiate_payment(
        self,
        amount,
        transaction_code,
        return_url,
        **kwargs
    ):

        if settings.SANDBOX:
            sandbox = "sandbox."
        else:
            sandbox = "payment."

        zp_api_request = (
            f"https://{sandbox}zarinpal.com/"
            "pg/v4/payment/request.json"
        )

        zp_api_startpay = (
            f"https://{sandbox}zarinpal.com/"
            "pg/StartPay/"
        )

        data = {
            "merchant_id": settings.MERCHANT,
            "amount": int(amount),
            "description": f"ShopLearning Payment - {transaction_code}",
            "mobile": "09129999999",
            "callback_url": return_url,
        }

        data = json.dumps(data)

        headers = {
            "content-type": "application/json",
            "content-length": str(len(data)),
            "accept": "application/json",
        }

        try:
            response = requests.post(
                zp_api_request,
                data=data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:

                response_data = response.json()

                if response_data.get("data", {}).get("code") == 100:

                    authority = response_data["data"]["authority"]

                    return redirect(
                        zp_api_startpay + authority
                    )

                return JsonResponse({
                    "status": False,
                    "code": response_data.get(
                        "data", {}
                    ).get("code"),
                    "message": response_data.get(
                        "errors",
                        response_data.get("data", {})
                    ),
                })

            return JsonResponse({
                "status": False,
                "message": "Request failed",
                "status_code": response.status_code,
            })

        except requests.exceptions.Timeout:
            return JsonResponse({
                "status": False,
                "code": "timeout",
            })

        except requests.exceptions.ConnectionError:
            return JsonResponse({
                "status": False,
                "code": "connection_error",
            })

        except Exception as e:
            return JsonResponse({
                "status": False,
                "error": str(e),
            })

    def verify_payment(
        self,
        authority,
        amount,
        transaction_code
    ):

        if not authority:
            return False, {
                "error": "Authority was not returned by Zarinpal"
            }

        if settings.SANDBOX:
            sandbox = "sandbox."
        else:
            sandbox = "payment."

        zp_api_verify = (
            f"https://{sandbox}zarinpal.com/"
            "pg/v4/payment/verify.json"
        )

        data = {
            "merchant_id": settings.MERCHANT,
            "amount": int(amount),
            "authority": authority,
        }

        data = json.dumps(data)

        headers = {
            "content-type": "application/json",
            "content-length": str(len(data)),
            "accept": "application/json",
        }

        try:
            response = requests.post(
                zp_api_verify,
                data=data,
                headers=headers,
                timeout=10
            )

            result = response.json()

            code = result.get("data", {}).get("code")

            if code in [100, 101]:
                return True, result

            return False, result

        except Exception as e:
            return False, {
                "error": str(e)
            }


class MellatPayment(BasePaymentGateway):

    def initiate_payment(
        self,
        amount,
        transaction_code,
        return_url
    ):
        pass

    def verify_payment(
        self,
        authority,
        amount,
        transaction_code
    ):
        return True, {}

    def payment_success(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pass

    def payment_fail(
        self,
        authority,
        amount,
        transaction_code,
        gateway_response
    ):
        pass


def pay_success_general(
    amount,
    transaction_code,
    gateway_response
):

    transaction_obj = Transaction.objects.get(
        transaction_code=transaction_code,
        amount=amount
    )

    invoice = transaction_obj.invoice

    if not invoice:
        transaction_obj.status = "failed"
        transaction_obj.response_date = gateway_response
        transaction_obj.save(
            update_fields=["status", "response_date"]
        )
        return

    order = invoice.order

    code = gateway_response.get("data", {}).get("code")

    # اگر قبلاً پرداخت شده، دوباره موجودی کم نکن
    if (
        transaction_obj.status == "complete"
        and invoice.status == "paid"
        and order.is_paid
    ):
        return

    if code in [100, 101]:

        try:

            with transaction.atomic():

                # کم کردن موجودی کالا
                decrease_stock_from_order(order)

                # پرداخت موفق
                transaction_obj.status = "complete"
                transaction_obj.response_date = gateway_response
                transaction_obj.save(
                    update_fields=[
                        "status",
                        "response_date"
                    ]
                )

                invoice.status = "paid"
                invoice.save(update_fields=["status"])

                order.status = 1
                order.is_paid = True
                order.save(
                    update_fields=[
                        "status",
                        "is_paid"
                    ]
                )

                # خالی کردن سبد خرید
                cart = Cart.objects.filter(
                    user=order.customer.user
                ).first()

                if cart:
                    cart.items.all().delete()
                    cart.has_applied_coupon = False
                    cart.save(
                        update_fields=[
                            "has_applied_coupon"
                        ]
                    )

        except ValueError as e:

            # پرداخت بانکی موفق بوده ولی موجودی کافی نیست
            transaction_obj.status = "failed"
            transaction_obj.response_date = {
                "payment_code": code,
                "error": str(e),
                "gateway_response": gateway_response,
            }
            transaction_obj.save(
                update_fields=[
                    "status",
                    "response_date"
                ]
            )

            invoice.status = "fail"
            invoice.save(update_fields=["status"])

            order.status = -3
            order.is_paid = False
            order.save(
                update_fields=[
                    "status",
                    "is_paid"
                ]
            )

        except Exception as e:

            transaction_obj.status = "failed"
            transaction_obj.response_date = {
                "payment_code": code,
                "error": str(e),
                "gateway_response": gateway_response,
            }
            transaction_obj.save(
                update_fields=[
                    "status",
                    "response_date"
                ]
            )

            invoice.status = "fail"
            invoice.save(update_fields=["status"])

            order.status = -3
            order.is_paid = False
            order.save(
                update_fields=[
                    "status",
                    "is_paid"
                ]
            )

    else:

        transaction_obj.status = "failed"
        transaction_obj.response_date = gateway_response
        transaction_obj.save(
            update_fields=[
                "status",
                "response_date"
            ]
        )

        invoice.status = "fail"
        invoice.save(update_fields=["status"])

        order.status = -2
        order.is_paid = False
        order.save(
            update_fields=[
                "status",
                "is_paid"
            ]
        )


def pay_fail_general(
    authority,
    amount,
    transaction_code,
    gateway_response
):

    transaction_obj = Transaction.objects.get(
        transaction_code=transaction_code,
        amount=amount
    )

    transaction_obj.status = "failed"
    transaction_obj.response_date = gateway_response
    transaction_obj.save(
        update_fields=[
            "status",
            "response_date"
        ]
    )

    invoice = transaction_obj.invoice

    if invoice:
        invoice.status = "fail"
        invoice.save(update_fields=["status"])

        order = invoice.order
        order.status = -2
        order.is_paid = False
        order.save(
            update_fields=[
                "status",
                "is_paid"
            ]
        )
