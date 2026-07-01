from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class B2BPartner(models.Model):
    """
    Modèle B2BPartner - partenaires entreprises/institutions.
    """
    PARTNER_TYPES = [
        ('school', 'École'),
        ('university', 'Université'),
        ('company', 'Entreprise'),
        ('ngo', 'ONG'),
        ('government', 'Gouvernement'),
        ('other', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('inactive', 'Inactif'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom de l'organisation")
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPES, verbose_name="Type de partenaire")
    
    # Contact information
    contact_person = models.CharField(max_length=200, verbose_name="Personne de contact")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")
    
    # Organization details
    tax_id = models.CharField(max_length=50, blank=True, verbose_name="Numéro fiscal")
    registration_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro d'enregistrement")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Contract details
    contract_start_date = models.DateField(null=True, blank=True, verbose_name="Date début contrat")
    contract_end_date = models.DateField(null=True, blank=True, verbose_name="Date fin contrat")
    contract_terms = models.TextField(blank=True, verbose_name="Conditions du contrat")
    
    # Billing
    billing_email = models.EmailField(blank=True, verbose_name="Email de facturation")
    billing_address = models.TextField(blank=True, verbose_name="Adresse de facturation")
    
    # Metadata
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Partenaire B2B"
        verbose_name_plural = "Partenaires B2B"
    
    def __str__(self):
        return f"{self.name} ({self.get_partner_type_display()})"


class B2BLicense(models.Model):
    """
    Modèle B2BLicense - licences pour écoles/institutions.
    """
    LICENSE_TYPES = [
        ('school', 'Licence École'),
        ('university', 'Licence Université'),
        ('enterprise', 'Licence Entreprise'),
        ('custom', 'Licence Personnalisée'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('suspended', 'Suspendu'),
        ('cancelled', 'Annulé'),
    ]
    
    partner = models.ForeignKey(B2BPartner, on_delete=models.CASCADE, related_name='licenses', verbose_name="Partenaire")
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPES, verbose_name="Type de licence")
    
    # License details
    license_key = models.CharField(max_length=100, unique=True, verbose_name="Clé de licence")
    name = models.CharField(max_length=200, verbose_name="Nom de la licence")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Pricing
    price_cfa = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Prix (FCFA)")
    billing_cycle = models.CharField(max_length=20, choices=[('monthly', 'Mensuel'), ('yearly', 'Annuel')], default='yearly', verbose_name="Cycle de facturation")
    
    # Limits
    max_students = models.IntegerField(verbose_name="Max étudiants", validators=[MinValueValidator(1)])
    max_teachers = models.IntegerField(verbose_name="Max enseignants", validators=[MinValueValidator(1)])
    max_courses = models.IntegerField(null=True, blank=True, verbose_name="Max cours")
    max_exams = models.IntegerField(null=True, blank=True, verbose_name="Max examens")
    
    # Features
    has_certificates = models.BooleanField(default=True, verbose_name="Certificats")
    has_analytics = models.BooleanField(default=True, verbose_name="Analytics")
    has_api_access = models.BooleanField(default=False, verbose_name="Accès API")
    has_custom_branding = models.BooleanField(default=False, verbose_name="Branding personnalisé")
    has_priority_support = models.BooleanField(default=True, verbose_name="Support prioritaire")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Statut")
    
    # Dates
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    
    # Usage tracking
    current_students = models.IntegerField(default=0, verbose_name="Étudiants actuels")
    current_teachers = models.IntegerField(default=0, verbose_name="Enseignants actuels")
    
    # Metadata
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Licence B2B"
        verbose_name_plural = "Licences B2B"
    
    def __str__(self):
        return f"{self.name} - {self.partner.name}"
    
    def is_active(self):
        """Check if license is currently active."""
        from django.utils import timezone
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date
    
    def days_remaining(self):
        """Calculate days remaining in license."""
        from django.utils import timezone
        today = timezone.now().date()
        if self.end_date:
            delta = self.end_date - today
            return max(0, delta.days)
        return 0
    
    def usage_percentage(self):
        """Calculate usage percentage based on student limit."""
        if self.max_students > 0:
            return (self.current_students / self.max_students) * 100
        return 0


class B2BUser(models.Model):
    """
    Modèle B2BUser - utilisateurs liés à une licence B2B.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('teacher', 'Enseignant'),
        ('student', 'Étudiant'),
    ]
    
    license = models.ForeignKey(B2BLicense, on_delete=models.CASCADE, related_name='users', verbose_name="Licence")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='b2b_memberships', verbose_name="Utilisateur")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Rôle")
    
    # Metadata
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='b2b_users_added', verbose_name="Ajouté par")
    
    class Meta:
        unique_together = ['license', 'user']
        ordering = ['-added_at']
        verbose_name = "Utilisateur B2B"
        verbose_name_plural = "Utilisateurs B2B"
    
    def __str__(self):
        return f"{self.user.email} - {self.license.name} ({self.get_role_display()})"


class B2BTransaction(models.Model):
    """
    Modèle B2BTransaction - transactions B2B.
    """
    TRANSACTION_TYPES = [
        ('license_purchase', 'Achat de licence'),
        ('license_renewal', 'Renouvellement de licence'),
        ('license_upgrade', 'Upgrade de licence'),
        ('add_seats', 'Ajout de places'),
        ('custom_service', 'Service personnalisé'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    
    partner = models.ForeignKey(B2BPartner, on_delete=models.CASCADE, related_name='transactions', verbose_name="Partenaire")
    license = models.ForeignKey(B2BLicense, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name="Licence")
    
    # Transaction details
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES, verbose_name="Type de transaction")
    amount_cfa = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Montant (FCFA)")
    
    # Payment details
    payment_method = models.CharField(max_length=50, blank=True, verbose_name="Méthode de paiement")
    payment_reference = models.CharField(max_length=200, blank=True, verbose_name="Référence de paiement")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Invoice
    invoice_number = models.CharField(max_length=100, blank=True, verbose_name="Numéro de facture")
    invoice_sent = models.BooleanField(default=False, verbose_name="Facture envoyée")
    
    # Metadata
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de complétion")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Transaction B2B"
        verbose_name_plural = "Transactions B2B"
    
    def __str__(self):
        return f"{self.partner.name} - {self.transaction_type} - {self.amount_cfa} FCFA"
