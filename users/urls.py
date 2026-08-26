from django.urls import path
from . import views
from .views import (
    show_register,
    show_login,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,  # این رو اضافه کنید
    CustomPasswordResetComplete,
    CustomPasswordResetDone
)

app_name = 'users'

urlpatterns = [
    path('show_register/', show_register, name='show_register'),
    path('show_login/', show_login, name='show_login'),

    # ___________________ forget password __________________________________________________________________#

    # صفحه درخواست فراموشی رمز
    path('forget_password/', CustomPasswordResetView.as_view(), name='forget_password'),

    # صفحه بعد از ارسال ایمیل
    path('password_reset_done/', CustomPasswordResetDone.as_view(), name='password_reset_done'),

    # صفحه تنظیم رمز جدید با توکن  <--- این مهمه
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # صفحه اتمام موفقیت‌آمیز
    path('reset/done/', CustomPasswordResetComplete.as_view(), name='password_reset_complete'),

    # ___________________ forget password ____________________________________________________________________#
]