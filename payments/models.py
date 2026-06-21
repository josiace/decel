from django.db import models
from django.conf import settings


class DCPack(models.Model):
    """
    Pack de DC disponible à l'achat.
    Géré par l'administrateur via l'interface admin.
    """
    name = models.CharField(max_length=100, verbose_name="Nom du pack")
    dc_amount = models.IntegerField(verbose_name="Montant DC", help_text="Nombre de DC inclus dans ce pack")
    price_cfa = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name="Prix (FCFA)")
    price_eur = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Prix (€) - OBSOLETE")
    stripe_price_id = models.CharField(
        max_length=255, blank=True,
        verbose_name="ID prix Stripe",
        help_text="ID du prix Stripe (price_xxx). Laisser vide si Stripe non configuré."
    )
    is_popular = models.BooleanField(default=False, verbose_name="Populaire", help_text="Affiche un badge 'Populaire'")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'price_cfa']
        verbose_name = "Pack DC"
        verbose_name_plural = "Packs DC"

    def __str__(self):
        return f"{self.name} — {self.dc_amount} DC ({self.price_cfa} FCFA)"

    @property
    def dc_per_cfa(self):
        """Nombre de DC par FCFA — utile pour afficher la valeur."""
        if self.price_cfa and self.price_cfa > 0:
            return round(self.dc_amount / float(self.price_cfa), 2)
        return 0


class DCPackOrder(models.Model):
    """
    Commande d'un pack DC. Supporte Stripe et paiements manuels.
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
        ('cancelled', 'Annulé'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('orange_money', 'Orange Money'),
        ('wave', 'Wave'),
        ('bank_transfer', 'Virement bancaire'),
        ('cash', 'Espèces'),
        ('recharge_code', 'Code de recharge'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dc_pack_orders',
        verbose_name="Utilisateur"
    )
    pack = models.ForeignKey(
        DCPack,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Pack acheté"
    )
    dc_amount = models.IntegerField(verbose_name="DC achetés")
    price_paid_cfa = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name="Prix payé (FCFA)")
    price_paid_eur = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Prix payé (€) - OBSOLETE")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='stripe', verbose_name="Méthode de paiement")
    stripe_session_id = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="ID session Stripe")
    stripe_payment_intent = models.CharField(max_length=255, blank=True, verbose_name="Payment Intent Stripe")
    transaction_reference = models.CharField(max_length=255, blank=True, verbose_name="Référence de transaction (Orange Money, Wave, etc.)")
    admin_notes = models.TextField(blank=True, verbose_name="Notes de l'administrateur")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de commande")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de complétion")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Commande DC"
        verbose_name_plural = "Commandes DC"

    def __str__(self):
        return f"{self.user.email} — {self.dc_amount} DC — {self.status}"


class RechargeCode(models.Model):
    """
    Codes de recharge DC générés par l'admin.
    Les utilisateurs peuvent acheter ces codes via des méthodes locales
    et les utiliser pour recharger leur compte.
    """
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('used', 'Utilisé'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
    ]
    
    code = models.CharField(max_length=20, unique=True, verbose_name="Code de recharge")
    dc_amount = models.IntegerField(verbose_name="Montant DC")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_recharge_codes')
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='used_recharge_codes')
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Date d'expiration")
    notes = models.TextField(blank=True, help_text="Notes sur ce code de recharge")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Code de recharge"
        verbose_name_plural = "Codes de recharge"

    def __str__(self):
        return f"{self.code} — {self.dc_amount} DC ({self.get_status_display()})"
    
    def is_valid(self):
        """Vérifie si le code est valide pour utilisation."""
        from django.utils import timezone
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
