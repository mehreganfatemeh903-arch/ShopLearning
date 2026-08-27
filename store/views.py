from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F, Case, When, FloatField
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from payment.models import Cart, CartItem, PaymentMethod, ShippingMethod

from store.forms import (
    VoteSubmitForm,
    ContactUsSubmitForm,
    CheckoutForm
)

from store.models import (
    VoteProduct,
    Product,
    ContactUs,
    BannerMain,
    Category,
    SpecialProduct,
    CategoryDiscount,
    Country,
    City,
    Customer,
    Coupon,
    Comment
)

from store.services import (
    check_stock,
    cart_items_is_empty,
    init_checkout_pyment_cart,
    init_checkout_cart
)

from store.untils import get_user_or_session


# ================================= HOME ======================================
def home_page(request):
    now = timezone.now()

    banners = BannerMain.objects.all()

    category = Category.objects.all()

    specials = SpecialProduct.objects.filter(
        quantity__gte=F('sold'),
        start_date__lte=now,
        end_date__gte=now
    ).select_related('product')

    category_discount = CategoryDiscount.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).select_related('category')

    # پیدا کردن اولین محصول دارای عکس برای هر دسته
    for discount in category_discount:
        discount.display_product = (
            Product.objects
            .filter(
                category=discount.category,
                image__isnull=False
            )
            .exclude(image='')
            .first()
        )

    context = {
        'banners': banners,
        'specials': specials,
        'category': category,
        'category_discount': category_discount,
    }

    return render(
        request,
        'main/home_store.html',
        context
    )

# ================================ CONTACT ====================================

def contact_page(request):
    if request.method == 'POST':

        forms = ContactUsSubmitForm(request.POST)

        if forms.is_valid():
            forms.save()

            messages.success(
                request,
                'Thank you for reaching out! We will contact you soon.'
            )

    return render(
        request,
        'main/contact_us.html'
    )


def about_page(request):
    return render(
        request,
        'main/about_us.html'
    )


# ================================= PRODUCTS ==================================

def products(request):
    list_products = Product.objects.all()

    query = request.GET.get('q')
    query_min_price = request.GET.get('min_price')
    query_max_price = request.GET.get('max_price')
    category_query = request.GET.get('category')

    if category_query and category_query != 'all':
        list_products = list_products.filter(
            category__id=category_query
        )

    if query:
        list_products = list_products.filter(
            name__icontains=query
        )

    list_products = list_products.annotate(
        effective_price=Case(
            When(
                discount_price__gt=0,
                then=F('discount_price')
            ),
            default=F('price'),
            output_field=FloatField()
        )
    )

    if query_min_price:
        list_products = list_products.filter(
            effective_price__gte=query_min_price
        )

    if query_max_price:
        list_products = list_products.filter(
            effective_price__lte=query_max_price
        )

    sorted_by = request.GET.get('sort_by')

    if sorted_by == 'price_asc':
        list_products = list_products.order_by(
            'effective_price'
        )

    elif sorted_by == 'price_desc':
        list_products = list_products.order_by(
            '-effective_price'
        )

    elif sorted_by == 'newest':
        list_products = list_products.order_by(
            '-created_at'
        )

    elif sorted_by == 'oldest':
        list_products = list_products.order_by(
            'created_at'
        )

    else:
        list_products = list_products.order_by(
            '-created_at'
        )

    paginator = Paginator(
        list_products,
        6
    )

    page_number = request.GET.get('page')

    try:
        products_page = paginator.page(page_number)

    except PageNotAnInteger:
        products_page = paginator.page(1)

    except EmptyPage:
        products_page = paginator.page(
            paginator.num_pages
        )

    context = {
    'products': products_page,
    'page_obj': products_page,
    'categories': Category.objects.all(),
    'current_query': query,
    'current_sort': sorted_by,
    'current_category': category_query,
}

    return render(
        request,
        'main/products.html',
        context
    )


def product_detail(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    votes = VoteProduct.objects.filter(
        is_publish=True,
        product=product
    )

    if request.method == 'POST':

        if not request.user.is_authenticated:
            return redirect(
                'users:show_login'
            )

        name = request.POST.get(
            'name',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        rating = request.POST.get(
            'rating'
        )

        description = request.POST.get(
            'description',
            ''
        ).strip()

        if name and rating and description:

            VoteProduct.objects.create(
                name=name,
                email=email,
                product=product,
                rating=int(rating),
                description=description,
                is_publish=False
            )

            Comment.objects.create(
                user=request.user,
                product=product,
                text=description,
                is_approved=False
            )

            messages.success(
                request,
                'Review submitted! Waiting for approval.'
            )

            return redirect(
                'store:product_detail',
                product_id=product_id
            )

        else:

            messages.error(
                request,
                'Please fill in all required fields.'
            )

    context = {
        'product': product,
        'votes': votes,
        'range': range(0, 6),
    }

    return render(
        request,
        'main/product_detail.html',
        context
    )


# ================================= CART ======================================

def cart_show(request):

    if request.user.is_authenticated:

        user = request.user
        session_key = None

    else:

        user = None

        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(
        user=user,
        Session_key=session_key
    )

    cart_items = cart.items.select_related(
        'product'
    ).all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }

    return render(
        request,
        'main/cart.html',
        context
    )


def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.user.is_authenticated:

        user = request.user
        session_key = None

    else:

        user = None

        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(
        user=user,
        Session_key=session_key
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'price_item': product.get_final_price(None)
        }
    )

    if not created:

        # بررسی موجودی قبل از افزایش تعداد
        new_quantity = cart_item.quantity + 1

        if not check_stock(
            product,
            new_quantity
        ):
            messages.error(
                request,
                f'Not enough stock available for "{product.name}".'
            )

            return redirect(
                'store:cart_show'
            )

        cart_item.quantity = new_quantity
        cart_item.save()

    messages.success(
        request,
        'Product added to cart successfully.'
    )

    return redirect(
        'store:cart_show'
    )


def update_cart(request, product_id):

    if request.method == 'POST':

        product = get_object_or_404(
            Product,
            id=product_id
        )

        try:
            quantity = int(
                request.POST.get(
                    'quantity',
                    1
                )
            )
        except (TypeError, ValueError):

            messages.error(
                request,
                'Invalid quantity.'
            )

            return redirect(
                'store:cart_show'
            )

        if quantity < 1:

            messages.error(
                request,
                'Quantity must be at least 1.'
            )

            return redirect(
                'store:cart_show'
            )

        check = check_stock(
            product,
            quantity
        )

        if check:

            user, session_key = get_user_or_session(
                request
            )

            cart, created = Cart.objects.get_or_create(
                user=user,
                Session_key=session_key
            )

            cart_item = get_object_or_404(
                CartItem,
                cart=cart,
                product=product
            )

            cart_item.quantity = quantity
            cart_item.save()

            messages.success(
                request,
                'Cart updated successfully.'
            )

        else:

            messages.error(
                request,
                f'Not enough stock available for "{product.name}".'
            )

    return redirect(
        'store:cart_show'
    )


def remove_from_cart(request, cart_item_id):

    if request.user.is_authenticated:

        cart_item = get_object_or_404(
            CartItem,
            id=cart_item_id,
            cart__user=request.user
        )

    else:

        session_key = request.session.session_key

        if not session_key:

            messages.error(
                request,
                'Session not found.'
            )

            return redirect(
                'store:cart_show'
            )

        cart_item = get_object_or_404(
            CartItem,
            id=cart_item_id,
            cart__session_key=session_key
        )

    cart_item.delete()

    messages.success(
        request,
        'Item removed from cart.'
    )

    return redirect(
        'store:cart_show'
    )


def apply_discount(request):

    if request.method == 'POST':

        discount_code = request.POST.get(
            'discount_code'
        )

        if not discount_code:

            messages.error(
                request,
                'Please enter a coupon code.'
            )

            return redirect(
                'store:cart_show'
            )

        try:

            coupon = Coupon.objects.get(
                code=discount_code,
                is_active=True
            )

            if coupon.is_valid():

                user, session_key = get_user_or_session(
                    request
                )

                cart, created = Cart.objects.get_or_create(
                    user=user,
                    Session_key=session_key
                )

                cart_items = cart.items.all()

                if not cart.has_applied_coupon:

                    for cart_item in cart_items:

                        coupon_discount = coupon.percentage
                        price = cart_item.price_item

                        price -= (
                            (
                                coupon_discount * price
                            ) / 100
                        )

                        cart_item.price_item = price
                        cart_item.save()

                    cart.has_applied_coupon = True
                    cart.save()

                    coupon.increment_use()

                    messages.success(
                        request,
                        'Coupon applied successfully.'
                    )

                else:

                    messages.error(
                        request,
                        'Coupon already used for this cart.'
                    )

            else:

                messages.error(
                    request,
                    'Coupon is not valid.'
                )

        except Coupon.DoesNotExist:

            messages.error(
                request,
                'Coupon code is incorrect.'
            )

    return redirect(
        'store:cart_show'
    )


# ================================ CHECKOUT ===================================

def checkout_show(request):

    # -----------------------------------------
    # 1. کاربر باید وارد شده باشد
    # -----------------------------------------
    if not request.user.is_authenticated:

        request.session[
            'checkout_redirect'
        ] = True

        return redirect(
            'users:show_login'
        )

    # -----------------------------------------
    # 2. پیدا کردن سبد خرید
    # -----------------------------------------
    cart_model, created_cart = Cart.objects.get_or_create(
        user=request.user,
        Session_key=None
    )

    # -----------------------------------------
    # 3. بررسی خالی نبودن سبد
    # -----------------------------------------
    try:

        cart_items_is_empty(
            cart_model
        )

    except ValueError:

        messages.error(
            request,
            'Your cart is empty.'
        )

        return redirect(
            'store:cart_show'
        )

    # -----------------------------------------
    # 4. بررسی موجودی کالاها
    # -----------------------------------------
    stock_errors = []

    for item in cart_model.items.select_related(
        'product'
    ).all():

        if not check_stock(
            item.product,
            item.quantity
        ):

            stock_errors.append(
                f'کالای «{item.product.name}» '
                f'به تعداد موردنظر موجود نیست.'
            )

    # -----------------------------------------
    # 5. پیدا کردن مشتری
    # -----------------------------------------
    customer, created = Customer.objects.get_or_create(
        user=request.user
    )

    # -----------------------------------------
    # 6. POST - ثبت سفارش
    # -----------------------------------------
    if request.method == 'POST':

        # اگر موجودی کافی نیست، اصلاً وارد پرداخت نشو
        if stock_errors:

            for error in stock_errors:
                messages.error(
                    request,
                    error
                )

            return redirect(
                'store:checkout'
            )

        form = CheckoutForm(
            request.POST,
            customer=customer
        )

        if form.is_valid():

            try:

                order_model, invoice, transaction_model = (
                    init_checkout_cart(
                        form,
                        cart_model
                    )
                )

                redirect_url = (
                    init_checkout_pyment_cart(
                        request,
                        order_model,
                        transaction_model
                    )
                )

                return redirect_url

            except ValueError as e:

                messages.error(
                    request,
                    f'⚠️ سفارش ثبت نشد: {str(e)}'
                )

                return redirect(
                    'store:cart_show'
                )

    else:

        form = CheckoutForm(
            customer=customer
        )

    # -----------------------------------------
    # 7. اطلاعات صفحه
    # -----------------------------------------
    country = Country.objects.all()

    city = City.objects.all()

    payment_methods = PaymentMethod.objects.filter(
        active=True
    )

    shipping_methods = ShippingMethod.objects.filter(
        active=True
    )

    context = {
        'country': country,
        'city': city,
        'payment_methods': payment_methods,
        'shipping_methods': shipping_methods,
        'cart_model': cart_model,
        'cart_items': cart_model.items.select_related(
            'product'
        ).all(),
        'cart_total': cart_model.get_total_price_cart(),
        'form': form,
        'stock_errors': stock_errors,
    }

    return render(
        request,
        'main/checkout.html',
        context
    )


# ================================= OTHER =====================================

def test(request):
    return render(
        request,
        'dashboard_admin/base/base_dashboard_admin.html'
    )


def fixed_sidebar(request):
    return render(
        request,
        'dashboard/fixed_sidebar.html'
    )


def admin_dashboard(request):
    return render(
        request,
        'main/dashboard.html'
    )


def dashboard_view(request):
    return render(
        request,
        'dashboard_admin/base/base_dashboard_admin.html'
    )