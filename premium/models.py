from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from skills.models import Subject


class PremiumService(models.Model):
    """
    Modèle PremiumService - services premium offerts par les contributeurs.
    """
    SERVICE_TYPES = [
        ('tutoring', 'Tutorat'),
        ('mentoring', 'Mentoring'),
        ('homework_correction', 'Correction de devoirs'),
        ('career_coaching', 'Coaching de carrière'),
        ('exam_prep', 'Préparation examen'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('paused', 'En pause'),
        ('inactive', 'Inactif'),
    ]
    
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='premium_services', verbose_name="Prestataire")
    
    # Service details
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES, verbose_name="Type de service")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='premium_services', verbose_name="Matière")
    
    # Pricing
    dc_price_per_hour = models.IntegerField(verbose_name="Prix par heure (DC)", validators=[MinValueValidator(1)])
    dc_price_per_session = models.IntegerField(null=True, blank=True, verbose_name="Prix par session (DC)", validators=[MinValueValidator(1)])
    
    # Availability
    duration_minutes = models.IntegerField(default=60, verbose_name="Durée (minutes)")
    is_online = models.BooleanField(default=True, verbose_name="En ligne")
    location = models.CharField(max_length=200, blank=True, verbose_name="Lieu (si présentiel)")
    
    # Requirements
    requirements = models.TextField(blank=True, verbose_name="Prérequis", help_text="Niveau requis, matériel, etc.")
    max_students_per_session = models.IntegerField(default=1, verbose_name="Max étudiants/session")
    
    # Scheduling
    available_days = models.JSONField(default=list, verbose_name="Jours disponibles", help_text="Liste des jours (ex: ['monday', 'wednesday'])")
    available_time_start = models.TimeField(verbose_name="Heure début disponibilité")
    available_time_end = models.TimeField(verbose_name="Heure fin disponibilité")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Service premium"
        verbose_name_plural = "Services premium"
    
    def __str__(self):
        return f"{self.title} - {self.provider.get_full_name|default:self.provider.username}"


class PremiumBooking(models.Model):
    """
    Modèle PremiumBooking - réservations de services premium.
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('no_show', 'Absent'),
    ]
    
    service = models.ForeignKey(PremiumService, on_delete=models.CASCADE, related_name='bookings', verbose_name="Service")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='premium_bookings', verbose_name="Étudiant")
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provided_bookings', verbose_name="Prestataire")
    
    # Scheduling
    scheduled_date = models.DateField(verbose_name="Date prévue")
    scheduled_time = models.TimeField(verbose_name="Heure prévue")
    duration_minutes = models.IntegerField(verbose_name="Durée (minutes)")
    
    # Payment
    dc_price = models.IntegerField(verbose_name="Prix DC")
    is_paid = models.BooleanField(default=False, verbose_name="Payé")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Meeting details (for online sessions)
    meeting_link = models.URLField(blank=True, verbose_name="Lien de réunion")
    meeting_notes = models.TextField(blank=True, verbose_name="Notes de réunion")
    
    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="Date d'annulation")
    cancellation_reason = models.TextField(blank=True, verbose_name="Raison d'annulation")
    
    # Rating
    rating = models.IntegerField(null=True, blank=True, verbose_name="Note", validators=[MinValueValidator(1)])
    review = models.TextField(blank=True, verbose_name="Avis")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        ordering = ['-scheduled_date', '-scheduled_time']
        verbose_name = "Réservation premium"
        verbose_name_plural = "Réservations premium"
    
    def __str__(self):
        return f"{self.service.title} - {self.student.email} - {self.scheduled_date}"


class PremiumServiceReview(models.Model):
    """
    Modèle PremiumServiceReview - avis sur les services premium.
    """
    booking = models.OneToOneField(PremiumBooking, on_delete=models.CASCADE, related_name='service_review', verbose_name="Réservation")
    service = models.ForeignKey(PremiumService, on_delete=models.CASCADE, related_name='reviews', verbose_name="Service")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='premium_reviews', verbose_name="Avisé")
    
    # Rating
    rating = models.IntegerField(verbose_name="Note", validators=[MinValueValidator(1)])
    
    # Review details
    communication = models.IntegerField(verbose_name="Communication", validators=[MinValueValidator(1)])
    expertise = models.IntegerField(verbose_name="Expertise", validators=[MinValueValidator(1)])
    helpfulness = models.IntegerField(verbose_name="Utilité", validators=[MinValueValidator(1)])
    punctuality = models.IntegerField(verbose_name="Ponctualité", validators=[MinValueValidator(1)])
    
    comment = models.TextField(verbose_name="Commentaire")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Avis service premium"
        verbose_name_plural = "Avis services premium"
    
    def __str__(self):
        return f"{self.reviewer.email} - {self.service.title} - {self.rating}/5"
    
    def average_rating(self):
        """Calcule la note moyenne."""
        return (self.rating + self.communication + self.expertise + self.helpfulness + self.punctuality) / 5
