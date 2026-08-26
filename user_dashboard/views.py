

from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
)

from payment.models import Transaction
from store.models import Order, Customer
from store.untils import get_tuple_status

from user_dashboard.forms import UserForm, PasswordForm
from users.decorator import PersonUserRequiredMixin
from users.models import PersonUser
from store.models import Comment
from store.models import Address

from asgiref.sync import sync_to_async


# ========================= Dashboard Helpers =========================


def get_transactions_sum(user):

    customer, created = Customer.objects.get_or_create(user=user)

    try:
        trans = Transaction.objects.filter(
            status='complete',
            invoice__order__customer=customer
        ).aggregate(total_amount=Sum('amount'))

        return trans['total_amount'] or 0

    except Exception:
        return 0



def sum_orders(user):

    customer, created = Customer.objects.get_or_create(user=user)

    return Order.objects.filter(customer=customer).count()



def get_date_user(user):
    return user.date_joined



def get_orders_user(user):

    orders = list(
        Order.objects.filter(
            customer__user=user
        ).values()[:5]
    )

    return orders


# ========================= Dashboard =========================

@login_required(login_url='users:show_login')
def dashboard_user(request):

    date_join = get_date_user(request.user)

    transactions_sum = get_transactions_sum(request.user)

    sum_order = sum_orders(request.user)

    list_orders = get_orders_user(request.user)

    context = {
        'transactions_sum': transactions_sum,
        'date_join': date_join,
        'sum_order': sum_order,
        'list_orders': list_orders
    }

    return render(request, 'dashboard_user/dashboard.html', context)


# ========================= Logout =========================

@login_required(login_url='users:show_login')
def sign_out_user(request):

    logout(request)

    return redirect('store:home')


# ========================= Profile =========================

@login_required(login_url='users:show_login')
def profile_user_show(request):

    user_instance = get_object_or_404(
        PersonUser,
        id=request.user.id
    )

    if request.method == 'POST':

        forms = UserForm(
            request.POST,
            instance=user_instance
        )

        if forms.is_valid():
            forms.save()

    else:
        forms = UserForm(instance=user_instance)

    return render(
        request,
        'dashboard_user/profile.html',
        {"forms": forms}
    )


# ========================= Change Password =========================
@login_required(login_url='users:show_login')
def change_profile_password(request):

    if request.method == 'POST':

        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            user_instance = get_object_or_404(PersonUser, id=request.user.id)
            forms = UserForm(instance=user_instance)
            return render(request, 'dashboard_user/profile.html', {
                'forms': forms,
                'password_error': 'Passwords do not match!'
            })

        if len(new_password) < 8:
            user_instance = get_object_or_404(PersonUser, id=request.user.id)
            forms = UserForm(instance=user_instance)
            return render(request, 'dashboard_user/profile.html', {
                'forms': forms,
                'password_error': 'Password must be at least 8 characters!'
            })

        user = request.user
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)

        return redirect('profile_user_show')

    return redirect('profile_user_show')
# ========================= Detail Order =========================

class DetailOrderView(PersonUserRequiredMixin, DetailView):

    model = Order

    template_name = 'dashboard_admin/detail_order_user.html'

    context_object_name = 'order'


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        order = self.get_object()

        context['order_invoices'] = order.invoices.all()

        context['order_details'] = order.detail.all()

        context['inboxes'] = order.invoices.all()

        return context


# ========================= Orders List =========================

class ListOrders(PersonUserRequiredMixin, ListView):

    model = Order

    template_name = 'dashboard_user/order_management.html'

    paginate_by = 10

    context_object_name = 'orders'

    def get_queryset(self):

        customer, created = Customer.objects.get_or_create(
            user=self.request.user
        )

        return Order.objects.filter(customer=customer)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['choices'] = get_tuple_status()

        return context





@login_required(login_url='users:show_login')
def comment_list_user(request):
    comments = Comment.objects.filter(user=request.user)
    return render(request, 'dashboard_user/comments.html', {'comments': comments})






@login_required(login_url='users:show_login')
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'dashboard_user/address_list.html', {'addresses': addresses})

@login_required(login_url='users:show_login')
def address_add(request):
    if request.method == 'POST':

        title = request.POST.get('title', '').strip()
        province = request.POST.get('province', '').strip()
        city = request.POST.get('city', '').strip()
        street = request.POST.get('street', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        is_default = request.POST.get('is_default') == 'on'

        # چک کردن فیلدهای خالی
        if not all([title, province, city, street, postal_code]):
            return render(request, 'dashboard_user/address_add.html', {
                'error': 'Please fill in all fields.',
                'data': request.POST  # برای نگه داشتن مقادیر قبلی
            })

        if is_default:
            Address.objects.filter(user=request.user).update(is_default=False)

        Address.objects.create(
            user=request.user,
            title=title,
            province=province,
            city=city,
            street=street,
            postal_code=postal_code,
            is_default=is_default,
        )
        return redirect('address_list_user')

    return render(request, 'dashboard_user/address_add.html')


@login_required(login_url='users:show_login')
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    return redirect('address_list_user')


@login_required(login_url='users:show_login')
def comment_list_user(request):
    comments = Comment.objects.filter(user=request.user)
    return render(request, 'dashboard_user/comments.html', {'comments': comments})