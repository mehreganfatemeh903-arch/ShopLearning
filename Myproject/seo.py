from django.http import HttpResponse


def robots_txt(request):
    content = """User-agent: *
Allow: /

Disallow: /admin/
Disallow: /admin_dashboard/
Disallow: /user_dashboard/
Disallow: /payment/

Sitemap: https://shoplearning-production.up.railway.app/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")
