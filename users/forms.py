from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms.widgets import Widget


class LoginForm(forms.Form):
    email=forms.EmailField(label='email',required=True)
    password=forms.CharField(widget=forms.PasswordInput)

User=get_user_model()

class RegisterForm(forms.Form):
    email=forms.EmailField(label="email",required=True)
    first_name=forms.CharField(max_length=30)
    last_name=forms.CharField(max_length=50)
    phone_number=forms.CharField(max_length=20,required=True)
    password=forms.CharField(required=True,widget=forms.PasswordInput)
    password_confirm=forms.CharField(required=True,widget=forms.PasswordInput)


    def clean_email(self):
        email=self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email is Exist')
        return email

    def clean(self):
        clean_data=super().clean()
        print("clean_data.get('password_confirm'):", clean_data.get('password_confirm'))
        print("clean_data.get('password')!:", clean_data.get('password'))

        if clean_data.get('password')!= clean_data.get('password_confirm'):
            return clean_data