from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.models import PersonUser
from store.models import Category, Product, Customer, CategoryDiscount, ProductDiscount, SpecialProduct, Coupon


class ProductDiscountTest(TestCase):

    def setUp(self) -> None :
       today = timezone.now().today()
       future_date = today + timedelta(days=10)
       past_date = today + timedelta(days=-10)

       self.user = PersonUser.objects.create_user("example@ex.com", '123456')
       self.customer = Customer.objects.create(User=self.user, phone='09999', address='sssss')

       self.ctegory = Category.objects.create(name='Electrics', slug='Electrics')

       self.product = Product.objects.create(Category=self.ctegory, name='Laptop', slug='laptops', price=1000, stock=10)

       self.category_discount = CategoryDiscount.objects.create(Category=self.ctegory, percentage=5, is_active=True,
                                                             start_date=past_date, end_date=future_date)

       self.product_discount = ProductDiscount.objects.create(Product=self.product, percentage=4, is_active=True,
                                                           start_date=past_date, end_date=future_date)

       self.special_product = SpecialProduct.objects.create(Product=self.product,
                                                         start_date=timezone.now() - timedelta(hours=5),
                                                         end_date=timezone.now() + timedelta(hours=5), sold=0,
                                                         quantity=10, special_percentage=3)

       self.coupon = Coupon.objects.create(code='TEST', percentage=2, max_use=10, start_date=past_date,
                                        end_date=future_date, is_general=True)


    def test_is_discount_product(self):
       self. assertTrue(self.product.is_discount_product())



   def test_final_price_apply(self):
      excepted_price = 1000
      excepted_price -= excepted_price * 0.05
      excepted_price -= excepted_price * 0.04
      excepted_price -= excepted_price * 0.03
      excepted_price -= excepted_price * 0.02
      # 1000*14%=140-1000=860
      final_price = self.Product.get_final_price(coupon_code='TEST')
      self.assertAlmostEqual(final_price, 2)
      final_price, round(excepted_price, 2)
