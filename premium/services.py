from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import PremiumService, PremiumBooking, PremiumServiceReview
from accounts.services import DCService


class PremiumServiceManager:
    """Service pour gérer les services premium."""
    
    @staticmethod
    @transaction.atomic
    def create_service(user, service_data):
        """
        Crée un nouveau service premium.
        
        Args:
            user: L'utilisateur (contributeur)
            service_data: Données du service
            
        Returns:
            PremiumService: Le service créé
        """
        service = PremiumService.objects.create(
            provider=user,
            **service_data
        )
        return service
    
    @staticmethod
    @transaction.atomic
    def book_service(student, service_id, scheduled_date, scheduled_time):
        """
        Réserve un service premium.
        
        Args:
            student: L'étudiant
            service_id: ID du service
            scheduled_date: Date de la réservation
            scheduled_time: Heure de la réservation
            
        Returns:
            tuple: (success: bool, message: str, booking: PremiumBooking or None)
        """
        from django.utils import timezone
        
        service = PremiumService.objects.get(id=service_id)
        
        # Vérifier que le service est actif
        if service.status != 'active':
            return False, "Ce service n'est pas disponible.", None
        
        # Vérifier que le prestataire n'est pas l'étudiant
        if service.provider == student:
            return False, "Vous ne pouvez pas réserver votre propre service.", None
        
        # Vérifier la disponibilité (jours)
        from datetime import datetime
        day_name = scheduled_date.strftime('%A').lower()
        if day_name not in service.available_days:
            return False, f"Le prestataire n'est pas disponible le {day_name}.", None
        
        # Vérifier la disponibilité (heures)
        if not (service.available_time_start <= scheduled_time <= service.available_time_end):
            return False, "L'heure demandée n'est pas dans les disponibilités du prestataire.", None
        
        # Vérifier qu'il n'y a pas déjà une réservation à cette heure
        existing_booking = PremiumBooking.objects.filter(
            service=service,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            status__in=['pending', 'confirmed']
        ).exists()
        
        if existing_booking:
            return False, "Ce créneau est déjà réservé.", None
        
        # Calculer le prix
        if service.dc_price_per_session:
            dc_price = service.dc_price_per_session
        else:
            # Prix par heure proratisé
            hours = service.duration_minutes / 60
            dc_price = int(service.dc_price_per_hour * hours)
        
        # Déduire les DC
        success, message, tx = DCService.deduct_dc(
            user=student,
            amount=dc_price,
            transaction_type='premium_service',
            description=f"Réservation : {service.title}"
        )
        
        if not success:
            return False, message, None
        
        # Créer la réservation
        booking = PremiumBooking.objects.create(
            service=service,
            student=student,
            provider=service.provider,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            duration_minutes=service.duration_minutes,
            dc_price=dc_price,
            is_paid=True,
            status='pending'
        )
        
        return True, "Réservation créée avec succès !", booking
    
    @staticmethod
    @transaction.atomic
    def confirm_booking(booking_id):
        """
        Confirme une réservation.
        
        Args:
            booking_id: ID de la réservation
            
        Returns:
            tuple: (success: bool, message: str)
        """
        booking = PremiumBooking.objects.get(id=booking_id)
        
        if booking.status != 'pending':
            return False, "Cette réservation n'est pas en attente."
        
        booking.status = 'confirmed'
        booking.save()
        
        return True, "Réservation confirmée."
    
    @staticmethod
    @transaction.atomic
    def start_session(booking_id, meeting_link=""):
        """
        Démarre une session.
        
        Args:
            booking_id: ID de la réservation
            meeting_link: Lien de réunion (optionnel)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        booking = PremiumBooking.objects.get(id=booking_id)
        
        if booking.status != 'confirmed':
            return False, "Cette réservation n'est pas confirmée."
        
        booking.status = 'in_progress'
        if meeting_link:
            booking.meeting_link = meeting_link
        booking.save()
        
        return True, "Session démarrée."
    
    @staticmethod
    @transaction.atomic
    def complete_session(booking_id, notes=""):
        """
        Termine une session.
        
        Args:
            booking_id: ID de la réservation
            notes: Notes de session (optionnel)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        booking = PremiumBooking.objects.get(id=booking_id)
        
        if booking.status != 'in_progress':
            return False, "Cette session n'est pas en cours."
        
        booking.status = 'completed'
        booking.meeting_notes = notes
        booking.save()
        
        return True, "Session terminée."
    
    @staticmethod
    @transaction.atomic
    def cancel_booking(booking_id, reason="", user=None):
        """
        Annule une réservation.
        
        Args:
            booking_id: ID de la réservation
            reason: Raison de l'annulation
            user: Utilisateur qui annule (pour vérification)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        booking = PremiumBooking.objects.get(id=booking_id)
        
        if booking.status in ['completed', 'cancelled', 'no_show']:
            return False, "Cette réservation ne peut plus être annulée."
        
        # Vérifier que l'utilisateur a le droit d'annuler
        if user and user != booking.student and user != booking.provider:
            return False, "Vous n'avez pas le droit d'annuler cette réservation."
        
        # Rembourser si annulé plus de 24h avant
        from django.utils import timezone
        from datetime import timedelta
        booking_datetime = timezone.datetime.combine(booking.scheduled_date, booking.scheduled_time)
        if booking_datetime - timezone.now() > timedelta(hours=24):
            DCService.add_dc(
                user=booking.student,
                amount=booking.dc_price,
                transaction_type='refund',
                description=f"Remboursement : {booking.service.title}"
            )
        
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = reason
        booking.save()
        
        return True, "Réservation annulée."
    
    @staticmethod
    @transaction.atomic
    def submit_review(booking_id, review_data):
        """
        Soumet un avis sur un service premium.
        
        Args:
            booking_id: ID de la réservation
            review_data: Données de l'avis
            
        Returns:
            tuple: (success: bool, message: str, review: PremiumServiceReview or None)
        """
        booking = PremiumBooking.objects.get(id=booking_id)
        
        if booking.status != 'completed':
            return False, "Vous ne pouvez noter que les sessions terminées.", None
        
        if PremiumServiceReview.objects.filter(booking=booking).exists():
            return False, "Vous avez déjà noté cette session.", None
        
        review = PremiumServiceReview.objects.create(
            booking=booking,
            service=booking.service,
            reviewer=booking.student,
            **review_data
        )
        
        return True, "Avis soumis avec succès !", review
    
    @staticmethod
    def get_provider_services(provider, status='active'):
        """
        Récupère les services d'un prestataire.
        
        Args:
            provider: Le prestataire
            status: Statut des services (optionnel)
            
        Returns:
            QuerySet: Services du prestataire
        """
        services = PremiumService.objects.filter(provider=provider)
        if status:
            services = services.filter(status=status)
        return services
    
    @staticmethod
    def get_provider_bookings(provider, status=None):
        """
        Récupère les réservations d'un prestataire.
        
        Args:
            provider: Le prestataire
            status: Statut des réservations (optionnel)
            
        Returns:
            QuerySet: Réservations du prestataire
        """
        bookings = PremiumBooking.objects.filter(provider=provider)
        if status:
            bookings = bookings.filter(status=status)
        return bookings.order_by('-scheduled_date', '-scheduled_time')
    
    @staticmethod
    def get_student_bookings(student, status=None):
        """
        Récupère les réservations d'un étudiant.
        
        Args:
            student: L'étudiant
            status: Statut des réservations (optionnel)
            
        Returns:
            QuerySet: Réservations de l'étudiant
        """
        bookings = PremiumBooking.objects.filter(student=student)
        if status:
            bookings = bookings.filter(status=status)
        return bookings.order_by('-scheduled_date', '-scheduled_time')
    
    @staticmethod
    def get_available_services(subject=None, service_type=None):
        """
        Récupère les services disponibles.
        
        Args:
            subject: Matière (optionnel)
            service_type: Type de service (optionnel)
            
        Returns:
            QuerySet: Services disponibles
        """
        services = PremiumService.objects.filter(status='active')
        if subject:
            services = services.filter(subject=subject)
        if service_type:
            services = services.filter(service_type=service_type)
        return services.select_related('provider', 'subject').order_by('-created_at')
