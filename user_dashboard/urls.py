from django.urls import path


from user_dashboard.views import dashboard_user, sign_out_user, profile_user_show, change_profile_password, \
    comment_list_user, address_delete, address_add, address_list,ListOrders, DetailOrderView

urlpatterns = [
    path('', dashboard_user, name='dashboard_user'),
    path('sign_out', sign_out_user, name='sign_out_user'),
    path('order_management', ListOrders.as_view(), name='order_management_user'),
    path('detail_order_show_user/<int:pk>', DetailOrderView.as_view(), name='detail_order_show_user'),
    path('profile', profile_user_show, name='profile_user_show'),
    path('change_profile_password', change_profile_password, name='change_profile_password'),
    path('comments', comment_list_user, name='comment_list_user'),
    path('address', address_list, name='address_list_user'),
    path('address/add', address_add, name='address_add_user'),
    path('address/delete/<int:pk>', address_delete, name='address_delete_user'),

]
