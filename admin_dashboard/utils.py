from store.models import Product, Order, Customer


def get_total_product():
    return Product.objects.all().count()



def get_total_orders():
    return Order.objects.all().count()



def get_total_members():
    return Customer.objects.all().count()


def get_last_orders():
    return Order.objects.order_by('-id'[:5])