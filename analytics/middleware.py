import uuid
from django.utils import timezone
from django.contrib.gis.geoip2 import GeoIP2
from user_agents import parse as parse_user_agent
from .models import PageView, UserSession


class AnalyticsMiddleware:
    """
    Middleware pour tracker les vues de pages et les sessions utilisateurs.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Essayer de charger GeoIP2 pour la localisation (optionnel)
        try:
            self.geoip2 = GeoIP2()
        except:
            self.geoip2 = None

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
            # Créer une nouvelle session
            ip_address = self.get_client_ip(request)
            user_agent_str = request.META.get('HTTP_USER_AGENT', '')

            # Parser user agent
            user_agent = parse_user_agent(user_agent_str)
            device_type = self.get_device_type(user_agent)
            browser = user_agent.browser.family if user_agent.browser else ''
            os = user_agent.os.family if user_agent.os else ''

            # Localisation (optionnel)
            country = ''
            city = ''
            if self.geoip2 and ip_address:
                try:
                    geo_data = self.geoip2.city(ip_address)
                    country = geo_data.get('country_name', '')
                    city = geo_data.get('city', '')
                except:
                    pass

            session = UserSession.objects.create(
                user=user,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent_str,
                device_type=device_type,
                browser=browser,
                os=os,
                country=country,
                city=city,
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
