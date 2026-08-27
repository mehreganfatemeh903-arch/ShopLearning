import os

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, FormView
from django.db.models import Q
from django.conf import settings

from store.models import (
    Order,
    OrderItem,
    Customer,
    Product,
    VoteProduct,
    ContactUs,
    Category,
    BannerMain,
    SettingSite,
    SpecialProduct,
    Coupon,
    CategoryDiscount,
    ProductDiscount,
)
from users.decorator import PersonUserRequiredMixin

from users.models import PersonUser

from store.untils import (
    get_tuple_status,
    STATUS_CHOICE,
    display_status
)

from .decorator import (
    is_super_user_required,
    SuperUserRequiredMixin
)

from .forms import (
    OrderStatusForm,
    CategoryForm,
    ProductForm,
    BannerForm,
    SpecialProductForm,
    CouponForm,
    CategoryDiscountForm,
    ProductDiscountForm
)

from .utils import (
    get_total_members,
    get_total_orders,
    get_total_product,
    get_last_orders
)


@is_super_user_required
def sign_out_admin(request):
    logout(request)
    return redirect('home')


@is_super_user_required
def dashboard_admin(request):
    context = {
        'total_members': get_total_members(),
        'total_orders': get_total_orders(),
        'total_product': get_total_product(),
        'last_orders': get_last_orders(),
    }
    return render(request, 'dashboard_admin/dashboard_main.html', context)


class ListUsers(SuperUserRequiredMixin, ListView):
    model = PersonUser
    template_name = 'dashboard_admin/list_users.html'
    paginate_by = 10
    context_object_name = 'users'
    ordering = ['-id']


class ListOrders(SuperUserRequiredMixin, ListView):
    model = Order
    template_name = 'dashboard_admin/all_orders_site.html'
    paginate_by = 10
    context_object_name = 'orders'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['choices'] = get_tuple_status()
        return context

    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        if order_id and status:
            order = get_object_or_404(Order, id=order_id)
            order.status = status
            order.save()
        return redirect('admin_dashboard:orders_list')




# برای admin
class DetailOrderAdminView(SuperUserRequiredMixin, DetailView):
    model = Order
    template_name = 'dashboard_admin/detail_order_user.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context['order_details'] = order.detail.all()
        context['inboxes'] = order.invoices.all()
        return context


# برای user
class DetailOrderView(PersonUserRequiredMixin, DetailView):
    model = Order
    template_name = 'dashboard_admin/detail_order_user.html'
    context_object_name = 'order'

    def get_queryset(self):
        customer, _ = Customer.objects.get_or_create(user=self.request.user)
        return Order.objects.filter(customer=customer)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context['order_details'] = order.detail.all()
        context['inboxes'] = order.invoices.all()
        return context




@is_super_user_required
def update_order_status(request):
    if request.method == 'POST':
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data['order_id']
            status = form.cleaned_data['status']
            order = get_object_or_404(Order, id=order_id)
            order.status = status
            order.save()
    return redirect('admin_dashboard:orders_list')


@is_super_user_required
def new_orders_site(request):
    customers = Customer.objects.all()

    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        order_notes = request.POST.get('note')
        status = request.POST.get('status')
        is_paid = request.POST.get('is-paid')
        products = request.POST.getlist('product[]')
        quantities = request.POST.getlist('qty[]')
        prices = request.POST.getlist('price[]')
        is_paid = True if is_paid == 'Yes' else False

        try:
            customer = Customer.objects.get(id=customer_id)
            order = Order.objects.create(
                customer=customer,
                note=order_notes,
                status=status,
                is_paid=is_paid,
            )
            total = 0
            for product_name, quantity, price in zip(products, quantities, prices):
                if product_name:
                    product = Product.objects.filter(name__icontains=product_name).first()
                    if product:
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=int(quantity)
                        )
                        total += int(price) * int(quantity)
            order.total_price = total
            order.save()
            messages.success(request, "Order created successfully.")
            return redirect('admin_dashboard:orders_list')

        except Exception as e:
            print(e)
            messages.error(request, f"Error: {e}")

    context = {
        'statuses': STATUS_CHOICE,
        'customer': customers,
    }
    return render(request, 'dashboard_admin/new_order_site.html', context)


def search_customers(request):
    query = request.GET.get("q", "")
    customers = Customer.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query)
    ).values("id", "user__last_name", "user__first_name")[:10]
    data = [
        {
            'id': c['id'],
            'text': f"{c['user__first_name']} {c['user__last_name']}"
        }
        for c in customers
    ]
    return JsonResponse(data, safe=False)


def search_product_item(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    ).values("id", "name", "description", "price")
    data = [
        {
            'id': p['id'],
            'text': f"{p['name']} -- {p['price']}"
        }
        for p in products
    ]
    return JsonResponse(data, safe=False)


class VoteManager(SuperUserRequiredMixin, ListView):
    paginate_by = 10
    context_object_name = 'votes'
    model = VoteProduct
    ordering = ['-id']
    template_name = 'dashboard_admin/vote_manager.html'


class InboxManager(SuperUserRequiredMixin, ListView):
    paginate_by = 10
    context_object_name = 'inboxes'
    model = ContactUs
    ordering = ['-id']
    template_name = 'dashboard_admin/inbox_show.html'


@is_super_user_required
def change_publish_vote(request, pk):
    vote = get_object_or_404(VoteProduct, id=pk)
    vote.is_publish = not vote.is_publish
    vote.save()
    return redirect('admin_dashboard:votes')


@is_super_user_required
def delete_banner(request, pk):
    banner = get_object_or_404(BannerMain, id=pk)
    banner.delete()
    return redirect('admin_dashboard:banners')


class BannerManagement(SuperUserRequiredMixin, ListView, FormView):
    context_object_name = 'banners'
    form_class = BannerForm
    template_name = 'dashboard_admin/new_banner_site.html'
    model = BannerMain
    success_url = reverse_lazy('admin_dashboard:banners')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forms'] = self.get_form()
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


@is_super_user_required
def get_coupon(request):
    coupons = Coupon.objects.all()
    edit_id = request.GET.get('edit')
    edit_instance = None
    if edit_id:
        edit_instance = get_object_or_404(Coupon, id=edit_id)

    if request.method == 'POST':
        form = CouponForm(request.POST, instance=edit_instance) if edit_instance else CouponForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
    else:
        form = CouponForm(instance=edit_instance) if edit_instance else CouponForm()

    return render(request, 'dashboard_admin/coupon.html', {'coupons': coupons, 'forms': form})


@is_super_user_required
def delete_coupon(request, pk):
    coupon = get_object_or_404(Coupon, id=pk)
    coupon.delete()
    return redirect('admin_dashboard:coupons')


@is_super_user_required
def special_products(request):
    if request.method == 'POST':
        form = SpecialProductForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Special Product added successfully.'
            )
            return redirect('admin_dashboard:special_products')

        messages.error(
            request,
            'Please correct the errors below.'
        )

    else:
        form = SpecialProductForm()

    special_products_list = SpecialProduct.objects.select_related(
        'product'
    ).order_by('-id')

    return render(
        request,
        'dashboard_admin/special_products.html',
        {
            'special_products': special_products_list,
            'form': form
        }
    )

@is_super_user_required
def special_product_delete(request, pk):
    special = get_object_or_404(SpecialProduct, id=pk)
    special.delete()
    return redirect('admin_dashboard:special_products')


@is_super_user_required
def category_add(request, id=None):
    category_object = None
    if id:
        category_object = get_object_or_404(Category, id=id)
    all_category = Category.objects.all()

    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category_object)
        if form.is_valid():
            form.save()
            messages.success(request, "Category Added Successfully")
        else:
            messages.error(request, "Category Failed")
    else:
        form = CategoryForm(instance=category_object)

    return render(request, 'dashboard_admin/category_add.html', {
        'all_category': all_category,
        'forms': form
    })


class CategoryList(SuperUserRequiredMixin, ListView):
    paginate_by = 10
    context_object_name = 'all_category'
    model = Category
    template_name = "dashboard_admin/category_list.html"
    ordering = ['-id']


class CategoryDelete(SuperUserRequiredMixin, View):
    def get(self, request, pk):
        category = get_object_or_404(Category, id=pk)
        if category.image:
            file_path = os.path.join(settings.MEDIA_ROOT, str(category.image))
            if os.path.exists(file_path):
                os.remove(file_path)
        category.delete()
        return redirect('admin_dashboard:categories')


@is_super_user_required
def product_add(request, id=None):
    category = Category.objects.all()
    product_object = None
    if id:
        product_object = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product_object)
        if form.is_valid():
            product = form.save(commit=False)
            product.discount_price = 0
            product.save()
            messages.success(request, "Product Added Successfully")
            return redirect('admin_dashboard:products')
        else:
            print(form.errors)
            messages.error(request, "Product Failed To Add")
    else:
        form = ProductForm(instance=product_object)

    return render(request, 'dashboard_admin/product_add.html', {
        'category': category,
        'forms': form
    })


class ProductList(SuperUserRequiredMixin, ListView):
    paginate_by = 10
    context_object_name = 'products'
    model = Product
    ordering = ['-id']
    template_name = "dashboard_admin/product_list.html"


@is_super_user_required
def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    product.delete()
    return redirect('admin_dashboard:products')


@is_super_user_required
def setting_admin(request):
    all_settings = SettingSite.objects.all()
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("setting"):
                setting_id = key.split("[")[1].split("]")[0]
                try:
                    setting = SettingSite.objects.get(id=setting_id)
                    setting.value = value
                    setting.save()
                except SettingSite.DoesNotExist:
                    messages.error(request, f"Setting with ID {setting_id} not found.")
        messages.success(request, "Settings Updated Successfully!")
    return render(request, 'dashboard_admin/site_setting.html', {"settings": all_settings})


@is_super_user_required
def create_default_site_setting(request):
    try:
        SettingSite.objects.create(key='site_name', value='')
        SettingSite.objects.create(key='site_description', value='')
        SettingSite.objects.create(key='site_logo', value='')
        SettingSite.objects.create(key='contact_email', value='')
        SettingSite.objects.create(key='social_links', value='')
    except Exception as e:
        print(e)
    return redirect('admin_dashboard:settings')


@is_super_user_required
def product_discount(request):
    products = Product.objects.all()
    edit_id = request.GET.get('edit')
    edit_instance = None
    if edit_id:
        edit_instance = get_object_or_404(ProductDiscount, id=edit_id)
    products_discount = ProductDiscount.objects.all()

    if request.method == "POST":
        form = ProductDiscountForm(request.POST, instance=edit_instance) if edit_instance else ProductDiscountForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
    else:
        form = ProductDiscountForm(instance=edit_instance) if edit_instance else ProductDiscountForm()

    return render(request, 'dashboard_admin/product_discount.html', {
        'products': products,
        'products_discount': products_discount,
        'forms': form
    })


@is_super_user_required
def category_discount(request):
    categories = Category.objects.all()
    edit_id = request.GET.get('edit')
    edit_instance = None
    if edit_id:
        edit_instance = get_object_or_404(CategoryDiscount, id=edit_id)
    categories_discount = CategoryDiscount.objects.all()

    if request.method == "POST":
        form = CategoryDiscountForm(request.POST, instance=edit_instance) if edit_instance else CategoryDiscountForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
    else:
        form = CategoryDiscountForm(instance=edit_instance) if edit_instance else CategoryDiscountForm()

    return render(request, 'dashboard_admin/category_discount.html', {
        "categories": categories,
        "categories_discount": categories_discount,
        "forms": form
    })


@is_super_user_required
def delete_category_discount(request, pk):
    category_discount_obj = get_object_or_404(CategoryDiscount, pk=pk)
    category_discount_obj.delete()
    return redirect('admin_dashboard:category_discounts')


@is_super_user_required
def delete_product_discount(request, pk):
    product_discount_obj = get_object_or_404(ProductDiscount, pk=pk)
    product_discount_obj.delete()
    return redirect('admin_dashboard:product_discounts')


@is_super_user_required
def seen_message(request, id):
    message = get_object_or_404(ContactUs, id=id)
    message.is_seen = True
    message.save()
    return redirect('admin_dashboard:inbox')