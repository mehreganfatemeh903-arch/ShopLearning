from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetDoneView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from users.forms import RegisterForm
from .models import PersonUser
from django.urls import reverse_lazy

from .utils import  merge_session_cart_to_user, redirect_user_dashboard


# Create your views here.


def show_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = PersonUser.objects.create_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone_number=form.cleaned_data['phone_number']
            )
            session_before=request.session.session_key
            login(request, user)
            merge_session_cart_to_user(request, user,session_before)

            messages.success(request, 'You Are Register SuccessFull')
            return redirect_user_dashboard(request)
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})


def show_login(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            session_before = request.session.session_key

            login(request, user)

            merge_session_cart_to_user(
                request,
                user,
                session_before
            )

            messages.success(
                request,
                'Login Successful'
            )

            return redirect_user_dashboard(request, user)

        else:

            messages.error(
                request,
                'Email or Password Is Wrong'
            )

    return render(request, 'main/login.html')


# کلاس ویوهای فراموشی رمز عبور
class CustomPasswordResetView(PasswordResetView):
    template_name = 'main/forget/forget_password.html'
    email_template_name = "main/forget/email_template.html"
    subject_template_name = "main/forget/email_subject.txt"  # اضافه کنید
    success_url = reverse_lazy('users:password_reset_done')  # اصلاح شده
    form_class = PasswordResetForm

    def form_valid(self, form):
        # برای دیباگ - نمایش ایمیل در ترمینال
        email = form.cleaned_data['email']
        print(f"Password reset requested for: {email}")
        return super().form_valid(form)


class CustomPasswordResetDone(PasswordResetDoneView):
    template_name = 'main/forget/forget_password_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "main/forget/password_confirm.html"
    success_url = reverse_lazy('users:password_reset_complete')  # اصلاح شده


class CustomPasswordResetComplete(PasswordResetCompleteView):
    template_name = "main/forget/password_reset_complete.html"