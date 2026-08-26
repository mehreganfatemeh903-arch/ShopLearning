from django import forms

from store.untils import STATUS_CHOICE, get_tuple_status  # توجه: untils نه untis
from store.models import Order, Category, Product, BannerMain, SpecialProduct, CategoryDiscount, ProductDiscount, Coupon


class OrderStatusForm(forms.Form):
    order_id = forms.IntegerField(widget=forms.HiddenInput())
    status = forms.ChoiceField(choices=get_tuple_status())  # حتما () داشته باشد


class OrderManualForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'status', 'total_price', 'note', 'method_out']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent','image']

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent == "":
            return None
        return parent

class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['category','slug','name','description','price','image','stock']


class BannerForm(forms.ModelForm):
    class Meta:
        model=BannerMain
        fields=['title','description','picture']



class SpecialProductForm(forms.ModelForm):
    class Meta:
        model=SpecialProduct
        fields=['product','start_date','end_date','special_percentage','quantity']



class CouponForm(forms.ModelForm):
    class Meta:
        model=Coupon
        fields=['code','percentage','start_date','end_date','category','max_use','time_use','is_general','products','is_active']


class CategoryDiscountForm(forms.ModelForm):
    class Meta:
        model = CategoryDiscount
        fields = ['percentage', 'category', 'start_date', 'end_date', 'is_active']


class ProductDiscountForm(forms.ModelForm):
    class Meta:
        model = ProductDiscount
        fields = ['percentage', 'product', 'start_date', 'end_date', 'is_active']
