"""Vues utilitaires SEO (robots.txt, etc.)."""
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import cache_page


@cache_page(60 * 60 * 24)
def robots_txt(request):
    """robots.txt dynamique avec URL du sitemap."""
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    if not site_url:
        site_url = request.build_absolute_uri('/').rstrip('/')

    lines = [
        'User-agent: *',
        'Allow: /$',
        'Allow: /register/',
        'Allow: /login/',
        'Disallow: /admin/',
        'Disallow: /dashboard/',
        'Disallow: /home/',
        'Disallow: /wallet/',
        'Disallow: /exams/',
        'Disallow: /learning/',
        'Disallow: /community/',
        'Disallow: /contributor/',
        'Disallow: /gamification/',
        'Disallow: /analytics/',
        'Disallow: /payments/',
        'Disallow: /api/',
        '',
        f'Sitemap: {site_url}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')
