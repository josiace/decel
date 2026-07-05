import uuid
import requests
from django.utils import timezone
from django.core.cache import cache
from user_agents import parse as parse_user_agent
from .models import PageView, UserSession


def get_country_from_ip(ip):
    if not ip or ip in ('127.0.0.1', 'localhost'):
        return 'ML'

    cache_key = f'geo_country_{ip}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        r = requests.get(
            f'http://ip-api.com/json/{ip}?fields=countryCode',
            timeout=2
        )
        country = r.json().get('countryCode', 'XX')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to get country for IP {ip}: {str(e)}")
        country = 'XX'

    cache.set(cache_key, country, 60 * 60 * 24)
    return country


class GeoLocationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ip:
            ip = ip.split(',')[0].strip()
        request.country_code = get_country_from_ip(ip)

        # Si l'utilisateur est connecté et que son country_code est vide ou différent, on le met à jour
        if request.user and request.user.is_authenticated:
            if not request.user.country_code or request.user.country_code != request.country_code:
                request.user.country_code = request.country_code
                request.user.save(update_fields=['country_code'])

        return self.get_response(request)


class AnalyticsMiddleware:
    """
    Middleware pour tracker les vues de pages et les sessions utilisateurs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ignorer les requêtes API, admin, static, media
        if self.should_ignore_request(request):
            return self.get_response(request)

        # Obtenir ou créer session_id
        session_id = self.get_or_create_session_id(request)

        # Créer ou mettre à jour la session utilisateur
        session = self.get_or_create_session(request, session_id)

        # Traiter la requête
        response = self.get_response(request)

        # Tracker la vue de page (après traitement pour obtenir le titre si possible)
        self.track_page_view(request, response, session_id, session)

        return response

    def should_ignore_request(self, request):
        """Détermine si la requête doit être ignorée."""
        ignore_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/api/analytics/',
            '/favicon.ico',
        ]
        return any(request.path.startswith(path) for path in ignore_paths)

    def get_or_create_session_id(self, request):
        """Obtient ou crée un ID de session unique."""
        if 'analytics_session_id' not in request.session:
            request.session['analytics_session_id'] = str(uuid.uuid4())
        return request.session['analytics_session_id']

    def get_or_create_session(self, request, session_id):
        """Obtient ou crée une session utilisateur."""
        user = request.user if request.user.is_authenticated else None

        try:
            session = UserSession.objects.get(session_id=session_id)
        except UserSession.DoesNotExist:
            ip_address = self.get_client_ip(request)
            user_agent_str = request.META.get('HTTP_USER_AGENT', '')

            user_agent = parse_user_agent(user_agent_str)
            device_type = self.get_device_type(user_agent)

            country_code = getattr(request, 'country_code', 'XX')

            session = UserSession.objects.create(
                user=user,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent_str,
                device_type=device_type,
                country=country_code,
                country_code=country_code,
                city='',
                entry_page=request.path,
            )

        return session

    def track_page_view(self, request, response, session_id, session):
        """Track une vue de page."""
        user = request.user if request.user.is_authenticated else None
        ip_address = self.get_client_ip(request)
        user_agent_str = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')

        # Parser user agent
        user_agent = parse_user_agent(user_agent_str)
        device_type = self.get_device_type(user_agent)
        browser = user_agent.browser.family if user_agent.browser else ''
        os = user_agent.os.family if user_agent.os else ''

        # Localisation
        country = session.country if session else ''
        country_code = session.country_code if session else getattr(request, 'country_code', 'XX')
        city = session.city if session else ''

        # Créer la vue de page
        PageView.objects.create(
            user=user,
            session_id=session_id,
            url=request.path,
            page_title=self.get_page_title(response),
            referrer=referrer,
            ip_address=ip_address,
            user_agent=user_agent_str,
            device_type=device_type,
            browser=browser,
            os=os,
            country=country,
            country_code=country_code,
            city=city,
        )

        # Mettre à jour la session
        session.page_views_count += 1
        session.journey_path = session.journey_path + [request.path] if session.journey_path else [request.path]
        session.unique_pages_count = len(set(session.journey_path))
        session.exit_page = request.path
        session.save()

    def get_client_ip(self, request):
        """Obtient l'adresse IP du client."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_device_type(self, user_agent):
        """Détermine le type d'appareil."""
        if user_agent.is_mobile:
            return 'Mobile'
        elif user_agent.is_tablet:
            return 'Tablet'
        elif user_agent.is_pc:
            return 'Desktop'
        elif user_agent.is_bot:
            return 'Bot'
        return 'Other'

    def get_page_title(self, response):
        """Essaie d'extraire le titre de la page de la réponse HTML."""
        if response.get('Content-Type', '').startswith('text/html'):
            try:
                content = response.content.decode('utf-8')
                if '<title>' in content and '</title>' in content:
                    start = content.find('<title>') + 7
                    end = content.find('</title>')
                    return content[start:end].strip()[:255]
            except:
                pass
        return ''
