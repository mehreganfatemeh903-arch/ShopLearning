from django import forms

from store.untils import STATUS_CHOICE, get_tuple_status
from store.models import (
    Order,
    Category,
    Product,
    BannerMain,
    SpecialProduct,
    CategoryDiscount,
    ProductDiscount,
    Coupon
)


class OrderStatusForm(forms.Form):
    order_id = forms.IntegerField(widget=forms.HiddenInput())
    status = forms.ChoiceField(choices=get_tuple_status())


class OrderManualForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'status', 'total_price', 'note', 'method_out']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent', 'image']

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent == "":
            return None
        return parent


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'slug', 'name', 'description', 'price', 'image', 'stock']


class BannerForm(forms.ModelForm):
    class Meta:
        model = BannerMain
        fields = ['title', 'description', 'picture']


class SpecialProductForm(forms.ModelForm):
    class Meta:
        model = SpecialProduct
        fields = [
            'product',
            'start_date',
            'end_date',
            'special_percentage',
            'quantity',
        ]
        widgets = {
            'start_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'end_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'special_percentage': forms.NumberInput(
                attrs={
                    'min': '0',
                    'max': '100',
                    'step': '0.01'
                }
            ),
            'quantity': forms.NumberInput(
                attrs={
                    'min': '1',
                    'step': '1'
                }
            ),
        }

    def clean_special_percentage(self):
        percentage = self.cleaned_data.get('special_percentage')

        if percentage is None:
            raise forms.ValidationError(
                'Discount percentage is required.'
            )

        if percentage < 0 or percentage > 100:
            raise forms.ValidationError(
                'Discount percentage must be between 0 and 100.'
            )

        return percentage

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')

        if quantity is None or quantity <= 0:
            raise forms.ValidationError(
                'Quantity must be greater than 0.'
            )

        return quantity

    def clean(self):
        cleaned_data = super().clean()

        product = cleaned_data.get('product')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError(
                    'End date must be after start date.'
                )

        if product:
            existing = SpecialProduct.objects.filter(product=product)

            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                self.add_error(
                    'product',
                    'This product already has a special product.'
                )

        return cleaned_data


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'code',
            'percentage',
            'start_date',
            'end_date',
            'category',
            'max_use',
            'time_use',
            'is_general',
            'products',
            'is_active'
        ]


class CategoryDiscountForm(forms.ModelForm):
    class Meta:
        model = CategoryDiscount
        fields = [
            'percentage',
            'category',
            'start_date',
            'end_date',
            'is_active'
        ]


class ProductDiscountForm(forms.ModelForm):
    class Meta:
        model = ProductDiscount
        fields = [
            'percentage',
            'product',
            'start_date',
            'end_date',
            'is_active'
        ]
