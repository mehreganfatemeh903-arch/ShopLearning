# from datetime import timezone
#
# from django.db import models
# from django.conf import settings
# from django.template.context_processors import request
# from unicodedata import category
#
#
# # Create your models here.
# class Customer(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     phone = models.CharField(max_length=50)
#     address = models.TextField()
#
#     def __str__(self):
#         return f"{self.user.email}"
#
#
# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(unique=True)
#     image = models.ImageField(upload_to='category/', blank=True, null=True)
#     parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='category', null=True, blank=True)
#
#
# class Product(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(unique=True)
#     description = models.TextField(blank=True, null=True)
#     price = models.BigIntegerField()
#     discount_price = models.FloatField(default=0)
#     image = models.ImageField(upload_to='products/', blank=True, null=True)
#     stock = models.PositiveIntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def save(self, *args, **kwargs):
#         if self.pk:
#             self.discount_price = self.get_final_price(None, False)
#             if self.discount_price == self.price:
#                 self.discount_price = 0
#         else:
#             self.discount_price = 0
#         super().save(*args, **kwargs)
#
#     def __str__(self):
#         return self.name
#
#     # def get_final_price(self, coupon_code=None, refresh_db=True):
#     #     if refresh_db:
#     #         self.refresh_from_db()
#     #     final_price = self.price
#     #     # Product_Discount
#     # try:
#     #     product_discount = self.product_discount
#     #     if product_discount.is_valid():
#     #         final_price -= (final_price * product_discount.percentage / 100)
#     # except  ProductDiscount.DoesNotExist:
#     #     pass
#     #
#     #     # CategoryDiscount
#     # try:
#     #
#     #     category_discount = self.category_discount
#     #     if category_discount.is_valid():
#     #         final_price -= (final_price * category_discount.percentage / 100)
#     # except  CategoryDiscount.DoesNotExist:
#     #     pass
#     #
#     # if hasattr(self, 'special_products') and self.special_products.is_valid():
#     #     dis = self.special_products.special_percentage
#     #     final_price -= (final_price * dis / 100)
#     #
#     # if coupon_code:
#     #     try:
#     #         coupon = Coupon.objects.get(code=coupon_code, is_valid=True)
#     #         if coupon.is_valid():
#     #             if coupon.is_general or self in coupon.category.all() or self in coupon.products.all():
#     #                 final_price -= (final_price * coupon.percentage / 100)
#     #                 coupon.increment_use()
#     #     except Coupon.DoesNotExist:
#     #         if final_price < 0:
#     #             return 0
#     #         else:
#     #             return final_price
#
#     def get_final_price(self, coupon_code=None, refresh_db=True):
#         if refresh_db:
#             self.refresh_from_db()
#
#         final_price = self.price
#
#         # Product Discount
#         try:
#             product_discount = self.product_discount
#             if product_discount.is_valid():
#                 final_price -= (final_price * product_discount.percentage / 100)
#
#         except ProductDiscount.DoesNotExist:
#             pass
#
#         # Category Discount
#         try:
#             category_discount = self.category.category_discount
#
#             if category_discount.is_valid():
#                 final_price -= (final_price * category_discount.percentage / 100)
#
#         except CategoryDiscount.DoesNotExist:
#             pass
#
#         # Special Product
#         if hasattr(self, 'special_products') and self.special_products.is_valid():
#             dis = self.special_products.special_percentage
#             final_price -= (final_price * dis / 100)
#
#         # Coupon
#         if coupon_code:
#             try:
#                 coupon = Coupon.objects.get(code=coupon_code, is_active=True)
#
#                 if coupon.is_valid():
#                     if (
#                             coupon.is_general or
#                             self in coupon.products.all() or
#                             self.category in coupon.category.all()
#                     ):
#                         final_price -= (final_price * coupon.percentage / 100)
#                         coupon.increment_use()
#
#             except Coupon.DoesNotExist:
#                 pass
#
#         if final_price < 0:
#             return 0
#
#         return final_price
#
#     def is_discount_product(self, coupon=False):
#         last_price = self.get_final_price(coupon)
#         if self.price > last_price:
#             return True
#         return False
#
#     def calculate_discount_percentage(self):
#         price1 = self.price  # 1000
#         price2 = self.get_final_price()  # 500
#         result = ((price1 - price2) / price1) * 100  # ((100-500)/100)*100->50
#         return result
#
#
# class SpecialProduct(models.Model):
#     product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='special_products')
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()
#     special_percentage = models.FloatField()
#     quantity = models.PositiveIntegerField(default=0)
#     sold = models.PositiveIntegerField(default=0)
#
#     def is_valid(self):
#         now = timezone.now()
#         return self.quantity > self.sold and self.start_date <= now <= self.end_date
#
#     def is_discount_product(self, coupon=False):
#         last_price = self.get_final_price(coupon)
#         if self.price > last_price:
#             return True
#         return False
#
#
# class ProductDiscount(models.Model):
#     product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='product_discount')
#     percentage = models.FloatField(help_text='Percentage Discount example 2.5%')
#     is_active = models.BooleanField(default=True)
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()
#
#     def is_valid(self):
#         today = timezone.now().date()
#         is_active = self.is_active
#         valid_time = self.start_date <= today <= self.end_data
#         if is_active and valid_time:
#             return True
#         else:
#             return False
#
#
# class CategoryDiscount(models.Model):
#     category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name='category_discount')
#     percentage = models.FloatField(help_text='Percentage Discount example 2.5%')
#     is_active = models.BooleanField(default=True)
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()
#
#     def is_valid(self):
#         today = timezone.now().date()
#         is_active = self.is_active
#         valid_time = self.start_date <= today <= self.end_data
#         if is_active and valid_time:
#             return True
#         else:
#             return False
#
#
# class Coupon(models.Model):
#     code = models.CharField(max_length=50, unique=True)
#     percentage = models.FloatField(help_text='Percentage Discount example 2.5%')
#     products = models.ManyToManyField(Product, related_name='coupons', blank=True)
#     category = models.ManyToManyField(Category, related_name='coupons', blank=True)
#     is_active = models.BooleanField(default=True)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     max_use = models.PositiveIntegerField(default=1)
#     time_use = models.PositiveIntegerField(default=0)
#     is_general = models.BooleanField(default=False)
#
#     def is_valid(self):
#         today = timezone.now().date()
#         is_active = self.is_active
#         valid_time = self.start_date <= today <= self.end_data
#         use = self.time_use < self.max_use
#         if is_active and valid_time and use:
#             return True
#         else:
#             return False
#
#     def increment_use(self):
#         if self.time_use < self.max_use:
#             self.time_use += 1
#             self.save()
#
#
# class VoteProduct(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField()
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='vote_product')
#     rating = models.PositiveIntegerField()
#     description = models.TextField()
#     is_publish = models.BooleanField(default=False)
#
#
# # class AddressCustomer(models.Model) :
# #     customer=""
# #     city=""
# #     address_line=""
# #
#
#
# # AddressCustomer can ba implemented related->Order
# # Province can ba implemented->Country
# class Country(models.Model):
#     name = models.CharField(max_length=50)
#     code = models.CharField(unique=True, max_length=30)  # Ir,GE
#
#     def __str__(self):
#         return self.name
#
#
# class City(models.Model):
#     name = models.CharField(max_length=50)
#     country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='city')
#
#     def __str__(self):
#         return self.name
#
#
# class Invoice(models.Model):
#     order = models.ForeignKey('store.order', on_delete=models.CASCADE, related_name='invoices')
#     amount = models.FloatField()
#     invoice_number = models.CharField(max_length=50, unique=True)
#     status = models.CharField(choices=[
#         ('pending', 'pending'),
#         ('paid', 'paid'),
#         ('fail', 'fail'),
#         ('refunded', 'refunded'),
#         ('expired', 'expired')
#     ])
#     created_at = models.DateTimeField(auto_now_add=True)
#     update_at = models.DateTimeField(auto_now=True)
#     expired_at = models.DateTimeField(null=True, blank=True)
#     gateway_response = models.JSONField(null=True, blank=True)
#
#     def __str__(self):
#         return f"{self.invoice_number} - {self.amount} - {self.status}"
#
#     def is_expired(self):
#         if self.expired_at and timezone.now() > self.expired_at:
#             return True
#         return False
#
#     def mark_as_paid(self):
#         self.status = 'paid'
#         self.order.is_paid = True
#         self.order.save()
#         self.save()
#
#     def make_as_fail(self):
#         self.status = 'fail'
#         self.save()
#
#
# class Order(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
#     is_paid = models.BooleanField(default=False)
#     total_price = models.BigIntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     status = models.IntegerField(default=-1)
#     note = models.CharField(null=True, blank=True)
#     method_out = models.BooleanField(default=True)
#     address_line = models.CharField(max_length=255, null=True, blank=True)
#     city = models.ForeignKey(City, on_delete=models.SET_NULL, related_name='orders_city', null=True)
#     post_code = models.CharField(max_length=20, null=True, blank=True)
#     shipping_method = models.ForeignKey('payment.ShippingMethod', on_delete=models.SET_NULL,
#                                         related_name='order_shipping_method', null=True)
#     payment_method = models.ForeignKey(
#         'payment.PaymentMethod',
#         on_delete=models.SET_NULL,
#         related_name='orders',
#         null=True
#     )
#
#     def get_status(self):
#         if self.status == 1:
#             return 'Processing'
#         elif self.status == 2:
#             return 'Shipping'
#         elif self.status == -1:
#             return 'Fail'
#         elif self.status == -2:
#             return 'Other Fail'
#         else:
#             return 'Other Status'
#
#     def __str__(self):
#         return f"Order is : {self.id}"
#
#
# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="detail", null=True, blank=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#
#     def __str__(self):
#         return f"{self.product.name}*{self.quantity}"
#
#
# class ContactUs(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField()
#     message = models.TextField()
#     seen = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)
#
#     def __str__(self):
#         return self.name
#
#
# class BannerMain(models.Model):
#     title = models.CharField(max_length=50)
#     description = models.CharField(max_length=100)
#     picture = models.ImageField(upload_to='banners/')
#
#
# class SettingSite(models.Model):
#     key = models.CharField(unique=True, max_length=100)
#     value = models.CharField(max_length=100)


from django.utils import timezone
from django.db import models
from django.conf import settings


class Customer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50)
    address = models.TextField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='category/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='category', null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.BigIntegerField()
    discount_price = models.FloatField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:
            self.discount_price = self.get_final_price(None, False)
            if self.discount_price == self.price:
                self.discount_price = 0
        else:
            self.discount_price = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_final_price(self, coupon_code=None, refresh_db=True):
        if refresh_db:
            self.refresh_from_db()

        final_price = self.price

        try:
            product_discount = self.product_discount
            if product_discount.is_valid():
                final_price -= (final_price * product_discount.percentage / 100)
        except ProductDiscount.DoesNotExist:
            pass

        try:
            category_discount = self.category.category_discount
            if category_discount.is_valid():
                final_price -= (final_price * category_discount.percentage / 100)
        except CategoryDiscount.DoesNotExist:
            pass

        if hasattr(self, 'special_products') and self.special_products.is_valid():
            dis = self.special_products.special_percentage
            final_price -= (final_price * dis / 100)

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if coupon.is_valid():
                    if (
                        coupon.is_general or
                        self in coupon.products.all() or
                        self.category in coupon.category.all()
                    ):
                        final_price -= (final_price * coupon.percentage / 100)
                        coupon.increment_use()
            except Coupon.DoesNotExist:
                pass

        return max(final_price, 0)

    def is_discount_product(self, coupon=False):
        return self.price > self.get_final_price(coupon)

    def calculate_discount_percentage(self):
        price2 = self.get_final_price()
        if self.price == 0:
            return 0
        return round(((self.price - price2) / self.price) * 100)


class SpecialProduct(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='special_products')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    special_percentage = models.FloatField()
    quantity = models.PositiveIntegerField(default=0)
    sold = models.PositiveIntegerField(default=0)

    def is_valid(self):
        now = timezone.now()
        return self.quantity > self.sold and self.start_date <= now <= self.end_date

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # after saving, update the product's discount_price
        self.product.save()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        # after deleting, reset the product's discount_price
        product.save()

    def __str__(self):
        return f"{self.product.name} - {self.special_percentage}%"


class ProductDiscount(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='product_discount')
    percentage = models.FloatField(help_text='Percentage Discount example 2.5%')
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def is_valid(self):
        today = timezone.now().date()
        return self.is_active and self.start_date.date() <= today <= self.end_date.date()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # after saving, update the product's discount_price
        self.product.save()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        # after deleting, reset the product's discount_price
        product.save()

    def __str__(self):
        return f"{self.product.name} - {self.percentage}%"


class CategoryDiscount(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name='category_discount')
    percentage = models.FloatField(help_text='Percentage Discount example 2.5%')
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def is_valid(self):
        today = timezone.now().date()
        return self.is_active and self.start_date.date() <= today <= self.end_date.date()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # after saving, update all products in this category
        for product in self.category.products.all():
            product.save()

    def delete(self, *args, **kwargs):
        category = self.category
        super().delete(*args, **kwargs)
        # after deleting, reset all products in this category
        for product in category.products.all():
            product.save()

    def __str__(self):
        return f"{self.category.name} - {self.percentage}%"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    percentage = models.FloatField(help_text='Percentage Discount example 2.5%')
    products = models.ManyToManyField(Product, related_name='coupons', blank=True)
    category = models.ManyToManyField(Category, related_name='coupons', blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    max_use = models.PositiveIntegerField(default=1)
    time_use = models.PositiveIntegerField(default=0)
    is_general = models.BooleanField(default=False)

    def is_valid(self):
        today = timezone.now().date()
        return (
            self.is_active and
            self.start_date <= today <= self.end_date and
            self.time_use < self.max_use
        )

    def increment_use(self):
        if self.time_use < self.max_use:
            self.time_use += 1
            self.save()

    def __str__(self):
        return self.code


class VoteProduct(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='vote_product')
    rating = models.PositiveIntegerField()
    description = models.TextField()
    is_publish = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.product.name}"


class Country(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(unique=True, max_length=30)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='city')

    def __str__(self):
        return self.name


class Invoice(models.Model):
    order = models.ForeignKey('store.order', on_delete=models.CASCADE, related_name='invoices')
    amount = models.FloatField()
    invoice_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(choices=[
        ('pending', 'pending'),
        ('paid', 'paid'),
        ('fail', 'fail'),
        ('refunded', 'refunded'),
        ('expired', 'expired')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.invoice_number} - {self.amount} - {self.status}"

    def is_expired(self):
        return bool(self.expired_at and timezone.now() > self.expired_at)

    def mark_as_paid(self):
        self.status = 'paid'
        self.order.is_paid = True
        self.order.save()
        self.save()

    def make_as_fail(self):
        self.status = 'fail'
        self.save()


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    total_price = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        (1, 'Processing'),
        (2, 'Shipping'),
        (-1, 'Fail'),
        (-2, 'Other Fail'),
        (0, 'Pending'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=-1)
    note = models.CharField(null=True, blank=True)
    method_out = models.BooleanField(default=True)
    address_line = models.CharField(max_length=255, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, related_name='orders_city', null=True)
    post_code = models.CharField(max_length=20, null=True, blank=True)
    shipping_method = models.ForeignKey('payment.ShippingMethod', on_delete=models.SET_NULL,
                                        related_name='order_shipping_method', null=True)
    payment_method = models.ForeignKey('payment.PaymentMethod', on_delete=models.SET_NULL,
                                       related_name='orders', null=True)

    def get_status(self):
        statuses = {1: 'Processing', 2: 'Shipping', -1: 'Fail', -2: 'Other Fail'}
        return statuses.get(self.status, 'Other Status')

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="detail", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField(default=0)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name




class SettingSite(models.Model):
    key = models.CharField(unique=True, max_length=100)
    value = models.CharField(max_length=100)



class BannerMain(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='banners/')
    is_cover = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ['-is_cover', 'order']

    def save(self, *args, **kwargs):
        if self.is_cover:
            BannerMain.objects.exclude(pk=self.pk).update(is_cover=False)
        super().save(*args, **kwargs)





class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(verbose_name='متن نظر')
    is_approved = models.BooleanField(default=False, verbose_name='تأیید شده')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product.name}"




class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=50, verbose_name='عنوان')  # مثلاً: خانه، محل کار
    province = models.CharField(max_length=100, verbose_name='استان')
    city = models.CharField(max_length=100, verbose_name='شهر')
    street = models.TextField(verbose_name='آدرس کامل')
    postal_code = models.CharField(max_length=10, verbose_name='کد پستی')
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.city}"
