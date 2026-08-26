from django import forms

from payment.models import ShippingMethod, PaymentMethod
from store.models import VoteProduct, ContactUs, Order, City


class VoteSubmitForm(forms.ModelForm):
    class Meta:
        model = VoteProduct
        fields = ['name', 'email', 'rating', 'description']


class ContactUsSubmitForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'message']  # ✅ email تکراری حذف شد


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address_line', 'city', 'post_code', 'shipping_method', 'payment_method']

    def __init__(self, *args, **kwargs):
        self.customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.all()
        self.fields['shipping_method'].queryset = ShippingMethod.objects.all()
        self.fields['payment_method'].queryset = PaymentMethod.objects.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.customer:
            instance.customer = self.customer
            if commit:
                instance.save()
                return instance
            return instance  # ✅ اضافه شد برای حالت commit=False
        return super().save(commit)  # ✅ اگر customer وجود نداشت