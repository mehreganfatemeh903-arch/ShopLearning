from django.urls import path


from payment.views import payment_callback


urlpatterns =[
       path('callback/<str:transaction_code>',payment_callback,name='payment_callback'),

]