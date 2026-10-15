import logging

from django.utils import timezone

from .models import VisitorTracking

logger = logging.getLogger(__name__)


class VisitorTrackingMiddleware:
    """Enregistre uniquement les visites HTML réussies, sans bloquer le site."""

    IGNORED_PREFIXES = (
        "/admin/", "/static/", "/media/", "/api/", "/favicon.ico",
        "/robots.txt", "/sitemap.xml",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.method != "GET"
            or not 200 <= response.status_code < 400
            or not response.get("Content-Type", "").startswith("text/html")
            or request.path.startswith(self.IGNORED_PREFIXES)
        ):
            return response

        try:
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
            ip_address = (
                forwarded.split(",", 1)[0].strip()
                if forwarded
                else request.META.get("REMOTE_ADDR", "")
            )
            now = timezone.now()
            VisitorTracking.objects.create(
                ip_address=ip_address or None,
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
                path=request.path,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key,
                visit_date=now.date(),
                visit_time=now.time(),
            )
        except Exception:
            logger.exception("Visitor tracking failed for %s", request.path)
        return response
