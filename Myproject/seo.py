from django.http import HttpResponse


def robots_txt(request):
    content = """User-agent: *
Allow: /

Disallow: /admin/
Disallow: /admin_dashboard/
Disallow: /user_dashboard/
Disallow: /payment/

Sitemap: http://127.0.0.1:8000/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")