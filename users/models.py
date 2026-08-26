from django.db import models
from django.contrib.auth.models import AbstractUser,AbstractBaseUser,PermissionsMixin,BaseUserManager

# Create your models here.
class CustomContextManager(BaseUserManager):
    def create_user(self,email,password=None,**extra):
        if not email:
            raise ValueError('Email Is Required')
        email=self.normalize_email(email)
        user=self.model(email=email,**extra)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,email,password,**extra):
        extra.setdefault('is_staff',True)
        extra.setdefault('is_superuser',True)

        if extra.get('is_staff') is not True:
            raise ValueError('is staff must be True')
        if extra.get('is_superuser') is not True:
            raise ValueError('is is superuser must be True')

        return self.create_user(email,password,**extra)


class PersonUser(AbstractBaseUser,PermissionsMixin):
    email=models.EmailField(unique=True,verbose_name='Emails')
    first_name=models.CharField(max_length=40,blank=True)
    last_name = models.CharField(max_length=40, blank=True)
    phone_number=models.CharField(max_length=20,unique=True,null=True,blank=True)
    is_staff=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined=models.DateTimeField(auto_now_add=True)
    objects=CustomContextManager()
    REQUIRED_FIELDS = ['phone_number']
    USERNAME_FIELD='email'




