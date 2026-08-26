from functools import wraps

from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin


def is_super_user_required(func):

    @wraps(func)

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('users:show_login')

        if not request.user.is_superuser:
            raise PermissionDenied(
                'You Have not Permission'
            )

        return func(request, *args, **kwargs)

    return wrapper


class SuperUserRequiredMixin(LoginRequiredMixin):

    login_url = 'users:show_login'

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('users:show_login')

        if not request.user.is_superuser:
            raise PermissionDenied(
                'You Have not Permission'
            )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )