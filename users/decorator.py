from django.contrib.auth.mixins import LoginRequiredMixin


class PersonUserRequiredMixin(LoginRequiredMixin):
    login_url = 'users:show_login'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,*args, **kwargs)