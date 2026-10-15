import ipaddress
import logging
import uuid

import requests
from django.core.cache import cache
from django.utils import timezone
from user_agents import parse as parse_user_agent

from .models import PageView, UserSession

logger = logging.getLogger(__name__)
GEO_CACHE_SECONDS = 60 * 60 * 24
TRACKABLE_CONTENT_TYPES = ("text/html",)


def _normalise_ip(value):
    """Return a valid IP address, or an empty string for untrusted input."""
    if not value:
        return ""
    try:
        return str(ipaddress.ip_address(value.strip()))
    except (ValueError, AttributeError):
        return ""


def get_request_ip(request):
    """
    Get a validated client IP. Forwarded headers are used because the app runs
    behind a reverse proxy; only the first address is considered.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    candidate = forwarded.split(",", 1)[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")
    return _normalise_ip(candidate)


def get_country_from_ip(ip):
    ip = _normalise_ip(ip)
    if not ip:
        return "XX"
    try:
        if ipaddress.ip_address(ip).is_loopback:
            return "ML"
    except ValueError:
        return "XX"

    cache_key = f"geo_country_{ip}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Do not let geolocation latency hold up a page request for long.
    country = "XX"
    try:
        response = requests.get(
            f"https://ip-api.com/json/{ip}?fields=status,countryCode",
            timeout=(0.4, 0.8),
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") == "success":
            candidate = payload.get("countryCode", "")
            if isinstance(candidate, str) and len(candidate) == 2:
                country = candidate.upper()
    except (requests.RequestException, ValueError, TypeError) as exc:
        logger.debug("IP geolocation unavailable: %s", exc)

    cache.set(cache_key, country, GEO_CACHE_SECONDS)
    return country


class GeoLocationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Avoid external geolocation calls for admin, API and non-page requests.
        path = request.path
        if request.method != "GET" or path.startswith(("/admin/", "/api/", "/static/", "/media/")):
            request.country_code = "XX"
            return self.get_response(request)

        ip = get_request_ip(request)
        request.country_code = get_country_from_ip(ip)

        user = getattr(request, "user", None)
        if user and user.is_authenticated and user.country_code != request.country_code:
            user.country_code = request.country_code
            user.save(update_fields=["country_code"])

        return self.get_response(request)


class AnalyticsMiddleware:
    """Track successful HTML page views, not API calls or asset requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self.should_ignore_request(request):
            return self.get_response(request)

        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if (
            request.method == "GET"
            and 200 <= response.status_code < 400
            and any(content_type.startswith(value) for value in TRACKABLE_CONTENT_TYPES)
        ):
            try:
                session_id = self.get_or_create_session_id(request)
                session = self.get_or_create_session(request, session_id)
                self.track_page_view(request, response, session_id, session)
            except Exception:
                # Analytics must never turn a successful page response into a 500.
                logger.exception("Page analytics tracking failed for %s", request.path)
        return response

    def should_ignore_request(self, request):
        return request.path.startswith((
            "/admin/", "/static/", "/media/", "/api/", "/favicon.ico",
            "/robots.txt", "/sitemap.xml",
        ))

    def get_or_create_session_id(self, request):
        if "analytics_session_id" not in request.session:
            request.session["analytics_session_id"] = str(uuid.uuid4())
        return request.session["analytics_session_id"]

    def get_or_create_session(self, request, session_id):
        user = request.user if request.user.is_authenticated else None
        session, created = UserSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                "user": user,
                "ip_address": get_request_ip(request) or None,
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                "device_type": self.get_device_type(parse_user_agent(request.META.get("HTTP_USER_AGENT", ""))),
                "country": getattr(request, "country_code", "XX"),
                "country_code": getattr(request, "country_code", "XX"),
                "city": "",
                "entry_page": request.path,
            },
        )
        # A session may begin anonymously and later authenticate.
        if not created and user and session.user_id != user.id:
            session.user = user
            session.save(update_fields=["user"])
        return session

    def track_page_view(self, request, response, session_id, session):
        user = request.user if request.user.is_authenticated else None
        user_agent_str = request.META.get("HTTP_USER_AGENT", "")
        user_agent = parse_user_agent(user_agent_str)
        country_code = session.country_code or getattr(request, "country_code", "XX")
        PageView.objects.create(
            user=user,
            session_id=session_id,
            url=request.path,
            page_title=self.get_page_title(response),
            referrer=request.META.get("HTTP_REFERER", ""),
            ip_address=get_request_ip(request) or None,
            user_agent=user_agent_str,
            device_type=self.get_device_type(user_agent),
            browser=user_agent.browser.family or "",
            os=user_agent.os.family or "",
            country=session.country or "",
            country_code=country_code,
            city=session.city or "",
        )
        session.page_views_count += 1
        journey = list(session.journey_path or [])
        journey.append(request.path)
        session.journey_path = journey[-100:]  # Bound stored journey size.
        session.unique_pages_count = len(set(journey))
        session.exit_page = request.path
        session.save(update_fields=[
            "page_views_count", "journey_path", "unique_pages_count", "exit_page",
        ])

    def get_device_type(self, user_agent):
        if user_agent.is_mobile:
            return "Mobile"
        if user_agent.is_tablet:
            return "Tablet"
        if user_agent.is_pc:
            return "Desktop"
        if user_agent.is_bot:
            return "Bot"
        return "Other"

    def get_page_title(self, response):
        if response.get("Content-Type", "").startswith("text/html"):
            try:
                content = response.content.decode("utf-8", errors="ignore")
                start = content.lower().find("<title>")
                end = content.lower().find("</title>", start + 7)
                if start != -1 and end != -1:
                    return content[start + 7:end].strip()[:255]
            except (AttributeError, UnicodeError):
                logger.debug("Could not extract page title", exc_info=True)
        return ""
