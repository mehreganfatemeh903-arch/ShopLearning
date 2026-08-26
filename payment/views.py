from http.client import HTTPResponse

from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404

from payment.models import Transaction
from payment.services import get_payment_service
from store.models import Invoice








# Create your views here.
def payment_callback(request, transaction_code):

    transaction = get_object_or_404(
        Transaction,
        transaction_code=transaction_code
    )

    gateway = get_payment_service(
        transaction.payment_method.identifier
    )

    authority = request.GET.get('Authority')

    result, data = gateway.verify_payment(
        authority,
        int(transaction.amount),
        transaction_code
    )

    if result:

        gateway.payment_success(
            transaction_code=transaction_code,
            authority=authority,
            amount=transaction.amount,
            gateway_response=data
        )

    else:

        gateway.payment_fail(
            transaction_code=transaction_code,
            authority=authority,
            amount=transaction.amount,
            gateway_response=data
        )

    context = {
        'transaction': transaction,
        'data': data,
        'result': result
    }

    return render(
        request,
        'dashboard_user/pay_result.html',
        context
    )