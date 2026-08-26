from wsgiref.util import request_uri

from django.shortcuts import redirect, render

from payment.models import Cart, CartItem


def merge_session_cart_to_user(request, user, session_before=None):
    if not session_before and not request.session.session_key:
        return

    final_session_key = session_before or request.session.session_key

    try:
        session_cart = Cart.objects.get(
            Session_key=final_session_key
        )
    except Cart.DoesNotExist:
        return

    user_cart, created = Cart.objects.get_or_create(
        user=user
    )

    for item in session_cart.items.all():

        cart_item, created_items = CartItem.objects.get_or_create(
            cart=user_cart,
            product=item.product,
            price_item=item.price_item,
            defaults={
                'quantity': item.quantity
            }
        )

        if not created_items:
            cart_item.quantity += item.quantity
            cart_item.save()

    session_cart.delete()


def get_role_user(user):

    if not user.is_authenticated:
        return "quest"

    if user.is_superuser:
        return "super_admin"

    if user.groups.filter(name='Admin').exists():
        return "admin"

    if user.groups.filter(name='Users').exists():
        return "users"

    if user.groups.filter(name='Finance').exists():
        return "finance"

    if user.groups.filter(name='support').exists():
        return "support"

    return "users"


def redirect_user_dashboard(request, user=None):

    if (
        'checkout_redirect' in request.session and
        request.user.is_authenticated
    ):
        del request.session['checkout_redirect']

        return redirect('store:cart_show')

    role = get_role_user(request.user)

    if request.user.is_authenticated:

        if role not in ['users', 'quest']:

            return redirect('admin_dashboard:dashboard')

        else:

            return render(
                request,
                'dashboard_user.html'
            )

    return render(
        request,
        'main/login.html'
    )
