from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from users.models import PersonUser
from store.models import (
    Category,
    Product,
    Customer,
    CategoryDiscount,
    ProductDiscount,
    SpecialProduct,
    Coupon,
)


class ProductDiscountTest(TestCase):

    def setUp(self):
        today = timezone.now()
        future_date = today + timedelta(days=10)
        past_date = today - timedelta(days=10)

        self.user = PersonUser.objects.create_user(
            email="example@ex.com",
            password="123456"
        )

        self.customer = Customer.objects.create(
            user=self.user,
            phone="09999",
            address="sssss",
        )

        self.category = Category.objects.create(
            name="Electrics",
            slug="Electrics",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Laptop",
            slug="laptops",
            price=1000,
            stock=10,
        )

        self.category_discount = CategoryDiscount.objects.create(
            category=self.category,
            percentage=5,
            is_active=True,
            start_date=past_date,
            end_date=future_date,
        )

        self.product_discount = ProductDiscount.objects.create(
            product=self.product,
            percentage=4,
            is_active=True,
            start_date=past_date,
            end_date=future_date,
        )

        self.special_product = SpecialProduct.objects.create(
            product=self.product,
            start_date=timezone.now() - timedelta(hours=5),
            end_date=timezone.now() + timedelta(hours=5),
            sold=0,
            quantity=10,
            special_percentage=3,
        )

        self.coupon = Coupon.objects.create(
            code="TEST",
            percentage=2,
            max_use=10,
            start_date=past_date.date(),
            end_date=future_date.date(),
            is_general=True,
        )

    def test_is_discount_product(self):
        self.assertTrue(
            self.product.is_discount_product()
        )

    def test_final_price_apply(self):
        final_price = self.product.get_final_price(
            coupon_code="TEST"
        )

        self.assertIsNotNone(final_price)