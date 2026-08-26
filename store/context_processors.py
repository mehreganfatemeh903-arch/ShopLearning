

from payment.models import Cart

def cart_count(request):
    count = 0

    # اگر کاربر لاگین است
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()

        # اگر کاربر قبلاً مهمان بوده و cart با Session_key داشته
        if not cart:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(Session_key=session_key).first()
    else:
        # کاربر مهمان
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        cart = Cart.objects.filter(Session_key=session_key).first()

    # محاسبه تعداد آیتم‌ها
    if cart:
        count = sum(item.quantity for item in cart.items.all())

    return {"cart_count": count}

