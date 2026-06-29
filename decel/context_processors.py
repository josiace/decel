"""Context processors globaux pour DECEL."""
from django.conf import settings
from django.templatetags.static import static


def seo(request):
    """Variables SEO disponibles dans tous les templates."""
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    if not site_url and request:
        site_url = request.build_absolute_uri('/').rstrip('/')

    og_image_path = static('images/icone.PNG')
    og_image = f"{site_url}{og_image_path}" if site_url else og_image_path

    canonical_url = request.build_absolute_uri(request.path) if request else site_url

    return {
        'SITE_URL': site_url,
        'SITE_NAME': settings.SITE_NAME,
        'SITE_TAGLINE': settings.SITE_TAGLINE,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
        'SITE_KEYWORDS': settings.SITE_KEYWORDS,
        'SITE_OG_IMAGE': og_image,
        'SITE_TWITTER_HANDLE': getattr(settings, 'SITE_TWITTER_HANDLE', ''),
        'SITE_LOCALE': settings.SITE_LOCALE,
        'SITE_LANGUAGE': settings.SITE_LANGUAGE,
        'CANONICAL_URL': canonical_url,
    }
