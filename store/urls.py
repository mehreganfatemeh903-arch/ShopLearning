from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [

    # ================= HOME =================

    path(
        '',
        views.home_page,
        name='home'
    ),

    # ================= PAGES =================

    path(
        'about/',
        views.about_page,
        name='about'
    ),

    path(
        'contact/',
        views.contact_page,
        name='contact'
    ),

    # ================= PRODUCTS =================

    path(
        'products/',
        views.products,
        name='products'
    ),

    path(
        'product/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),

    # ================= CART =================

    path(
        'cart/',
        views.cart_show,
        name='cart_show'
    ),

    path(
        'cart/add/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'cart/update/<int:product_id>/',
        views.update_cart,
        name='update_cart'
    ),

    path(
        'cart/remove/<int:cart_item_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path(
        'apply-discount/',
        views.apply_discount,
        name='apply_discount'
    ),

    # ================= CHECKOUT =================

    path(
        'checkout/',
        views.checkout_show,
        name='checkout'
    ),

    # ================= TEST =================

    path(
        'test/',
        views.test,
        name='test'
    ),

    path(
        'dashboard/fixed/',
        views.fixed_sidebar,
        name='fixed_sidebar'
    ),

    path(
        'admin/dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'test/dashboard/',
        views.dashboard_view,
        name='dashboard_view'
    ),
]