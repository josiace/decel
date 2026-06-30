from django.utils import timezone
from .models import VisitorTracking


class VisitorTrackingMiddleware:
    """
    Middleware pour tracker les visiteurs du site.
    Enregistre chaque visite avec date, heure et informations de base.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ne pas tracker les requêtes admin, static, media ou API
        if any(path in request.path for path in ['/admin/', '/static/', '/media/', '/api/']):
            return self.get_response(request)
        
        # Ne tracker que les requêtes GET
        if request.method != 'GET':
            return self.get_response(request)
        
        # Obtenir l'adresse IP
        ip_address = self.get_client_ip(request)
        
        # Obtenir l'heure actuelle
        now = timezone.now()
        visit_date = now.date()
        visit_time = now.time()
        
        # Créer l'enregistrement de visite
        try:
            VisitorTracking.objects.create(
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                path=request.path,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key,
                visit_date=visit_date,
                visit_time=visit_time
            )
        except Exception:
            # Si erreur, ignorer pour ne pas bloquer la requête
            pass
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """
        Obtenir l'adresse IP du client.
        Gère les proxies et load balancers.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
