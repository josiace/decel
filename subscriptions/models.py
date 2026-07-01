from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class SubscriptionPlan(models.Model):
    """
    Modèle SubscriptionPlan - plans d'abonnement disponibles.
    """
    PLAN_TYPES = [
        ('free', 'Gratuit'),
        ('premium', 'Premium'),
        ('pro', 'Professionnel'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Mensuel'),
        ('yearly', 'Annuel'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du plan")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, verbose_name="Type de plan")
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly', verbose_name="Cycle de facturation")
    
    # Pricing
    dc_price = models.IntegerField(verbose_name="Prix en DC", help_text="Prix en DC pour ce plan")
    stripe_price_id = models.CharField(max_length=255, blank=True, verbose_name="ID prix Stripe")
    
    # Features (JSON field for flexibility)
    features = models.JSONField(default=dict, verbose_name="Fonctionnalités", help_text="Liste des fonctionnalités incluses")
    
    # Limits
    max_courses_per_month = models.IntegerField(null=True, blank=True, verbose_name="Max cours/mois")
    max_exams_per_month = models.IntegerField(null=True, blank=True, verbose_name="Max examens/mois")
    max_tds_per_month = models.IntegerField(null=True, blank=True, verbose_name="Max TDs/mois")
    
    # Premium features
    has_certificates = models.BooleanField(default=False, verbose_name="Certificats")
    has_mentoring = models.BooleanField(default=False, verbose_name="Mentoring")
    has_analytics = models.BooleanField(default=False, verbose_name="Analytics avancés")
    has_priority_support = models.BooleanField(default=False, verbose_name="Support prioritaire")
    has_ad_free = models.BooleanField(default=False, verbose_name="Sans publicité")
    
    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_popular = models.BooleanField(default=False, verbose_name="Populaire")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        ordering = ['order', 'dc_price']
        verbose_name = "Plan d'abonnement"
        verbose_name_plural = "Plans d'abonnement"
    
    def __str__(self):
        return f"{self.name} ({self.get_billing_cycle_display()}) - {self.dc_price} DC"


class UserSubscription(models.Model):
    """
    Modèle UserSubscription - suit les abonnements des utilisateurs.
    """
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('cancelled', 'Annulé'),
        ('expired', 'Expiré'),
        ('pending', 'En attente'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions', verbose_name="Utilisateur")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, verbose_name="Plan")
    
    # Subscription details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    start_date = models.DateTimeField(verbose_name="Date de début")
    end_date = models.DateTimeField(verbose_name="Date de fin")
    auto_renew = models.BooleanField(default=True, verbose_name="Renouvellement automatique")
    
    # Payment tracking
    stripe_subscription_id = models.CharField(max_length=255, blank=True, verbose_name="ID abonnement Stripe")
    last_payment_date = models.DateTimeField(null=True, blank=True, verbose_name="Date du dernier paiement")
    next_payment_date = models.DateTimeField(null=True, blank=True, verbose_name="Date du prochain paiement")
    
    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="Date d'annulation")
    cancellation_reason = models.TextField(blank=True, verbose_name="Raison de l'annulation")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Abonnement utilisateur"
        verbose_name_plural = "Abonnements utilisateurs"
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"
    
    def is_active(self):
        """Check if subscription is currently active."""
        from django.utils import timezone
        return self.status == 'active' and self.end_date > timezone.now()
    
    def days_remaining(self):
        """Calculate days remaining in subscription."""
        from django.utils import timezone
        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return 0


class SubscriptionTransaction(models.Model):
    """
    Modèle SubscriptionTransaction - suit les transactions d'abonnement.
    """
    TRANSACTION_TYPES = [
        ('subscription_start', 'Début d\'abonnement'),
        ('subscription_renewal', 'Renouvellement d\'abonnement'),
        ('subscription_upgrade', 'Upgrade d\'abonnement'),
        ('subscription_downgrade', 'Downgrade d\'abonnement'),
        ('subscription_cancel', 'Annulation d\'abonnement'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription_transactions', verbose_name="Utilisateur")
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='transactions', verbose_name="Abonnement")
    
    # Transaction details
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES, verbose_name="Type de transaction")
    dc_amount = models.IntegerField(verbose_name="Montant DC")
    
    # Stripe details
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, verbose_name="ID Payment Intent Stripe")
    
    # Plan details (snapshot)
    plan_name = models.CharField(max_length=100, verbose_name="Nom du plan")
    plan_type = models.CharField(max_length=20, verbose_name="Type de plan")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Transaction d'abonnement"
        verbose_name_plural = "Transactions d'abonnement"
    
    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.dc_amount} DC"
