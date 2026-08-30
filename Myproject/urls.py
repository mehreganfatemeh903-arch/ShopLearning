from django.contrib import admin
from .seo import robots_txt
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

from store.sitemaps import StaticViewSitemap, ProductSitemap


sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('store.urls')),

    path('admin_dashboard/', include('admin_dashboard.urls')),

    path('users/', include('users.urls')),

    path('payment/', include('payment.urls')),

    path('user_dashboard/', include('user_dashboard.urls')),

    # ================= SEO =================
    path(
        'robots.txt',
        robots_txt,
        name='robots_txt'
    ),

    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'
    ),
]


urlpatterns += [
    re_path(
        r'^media/(?P<path>.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT}
    ),
]
