from django.urls import path

from .views import (
    dashboard_admin,
    ListUsers,
    ListOrders,
    DetailOrderView,
    DetailOrderAdminView,
    new_orders_site,
    update_order_status,
    search_customers,
    search_product_item,
    InboxManager,
    seen_message,
    VoteManager,
    change_publish_vote,
    sign_out_admin,
    BannerManagement,
    delete_banner,
    CategoryList,
    CategoryDelete,
    category_add,
    ProductList,
    product_add,
    delete_product,
    setting_admin,
    create_default_site_setting,
    get_coupon,
    delete_coupon,
    category_discount,
    delete_category_discount,
    product_discount,
    delete_product_discount,
    special_products,
    special_product_delete,
)

app_name = "admin_dashboard"

urlpatterns = [

    # ---------------- Dashboard ----------------
    path("", dashboard_admin, name="dashboard"),

    # ---------------- Users ----------------
    path("users/", ListUsers.as_view(), name="users_list"),

    # ---------------- Orders ----------------
    path("orders/", ListOrders.as_view(), name="orders_list"),
    path("orders/<int:pk>/", DetailOrderAdminView.as_view(), name="order_detail"),
    path("orders/new/", new_orders_site, name="new_orders"),
    path("orders/update-status/", update_order_status, name="order_update_status"),

    # ---------------- Search ----------------
    path("search/customers/", search_customers, name="search_customers"),
    path("search/products/", search_product_item, name="search_products"),

    # ---------------- Inbox ----------------
    path("inbox/", InboxManager.as_view(), name="inbox"),
    path("inbox/seen/<int:id>/", seen_message, name="message_seen"),

    # ---------------- Votes ----------------
    path("votes/", VoteManager.as_view(), name="votes"),
    path("votes/publish/<int:pk>/", change_publish_vote, name="vote_publish"),

    # ---------------- Auth ----------------
    path("logout/", sign_out_admin, name="logout"),

    # ---------------- Banners ----------------
    path("banners/", BannerManagement.as_view(), name="banners"),
    path("banners/delete/<int:pk>/", delete_banner, name="banner_delete"),

    # ---------------- Categories ----------------
    path("categories/", CategoryList.as_view(), name="categories"),
    path("categories/add/", category_add, name="category_add"),
    path("categories/<int:id>/edit/", category_add, name="category_edit"),
    path("categories/delete/<int:pk>/", CategoryDelete.as_view(), name="category_delete"),

    # ---------------- Products ----------------
    path("products/", ProductList.as_view(), name="products"),
    path("products/add/", product_add, name="product_add"),
    path("products/<int:id>/edit/", product_add, name="product_edit"),
    path("products/delete/<int:pk>/", delete_product, name="product_delete"),

    # ---------------- Settings ----------------
    path("settings/", setting_admin, name="settings"),
    path("settings/init/", create_default_site_setting, name="settings_init"),

    # ---------------- Coupons ----------------
    path("coupons/", get_coupon, name="coupons"),
    path("coupons/delete/<int:pk>/", delete_coupon, name="coupon_delete"),

    # ---------------- Discounts ----------------
    path("discounts/categories/", category_discount, name="category_discounts"),
    path("discounts/categories/delete/<int:pk>/", delete_category_discount, name="category_discount_delete"),
    path("discounts/products/", product_discount, name="product_discounts"),
    path("discounts/products/delete/<int:pk>/", delete_product_discount, name="product_discount_delete"),

    # ---------------- Special Products ----------------
    path("special-products/", special_products, name="special_products"),
    path("special-products/delete/<int:pk>/", special_product_delete, name="special_product_delete"),
]