from django import forms
from users.models import PersonUser


class UserForm(forms.ModelForm):
    class Meta:

        model=PersonUser
        fields=['first_name','last_name','phone_number','email']



class PasswordForm(forms.ModelForm):
   new_password=forms.CharField(label='new_password',widget=forms.PasswordInput(attrs={'class':'form_control'}))
   confirm_password = forms.CharField(label='confirm_password', widget=forms.PasswordInput(attrs={'class': 'form_control'}))

   def clean(self):
       cleans_data=super().clean()
       new_pass=cleans_data.get('new_password')
       confirm_password = cleans_data.get('confirm_password')
       if new_pass !=confirm_password:
           raise forms.ValidationError('confirm password not match new password')
       if len(new_pass)<8:
           raise forms.ValidationError('password must be last at 8 char long')
       return cleans_data