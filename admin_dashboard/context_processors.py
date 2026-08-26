from store.models import ContactUs


def notification_count(request):
    if request.user.is_authenticated and request.user.is_superuser:
        count = ContactUs.objects.filter(seen=False).count()
    else:
        count = 0
    return {'notification_count': count}