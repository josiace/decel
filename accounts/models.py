from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import transaction


class Country(models.Model):
    """
    Modèle de pays - liste des pays disponibles pour l'inscription.
    Géré par l'administrateur.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du pays", help_text="Nom du pays")
    code = models.CharField(max_length=3, unique=True, verbose_name="Code ISO", help_text="Code ISO du pays (ex: FRA, USA)")
    is_active = models.BooleanField(default=True, verbose_name="Actif", help_text="Cocher pour rendre le pays disponible à l'inscription")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        ordering = ['name']
        verbose_name = "Pays"
        verbose_name_plural = "Pays"

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Modèle d'utilisateur personnalisé pour DECEL.
    Étend le modèle AbstractUser de Django avec des champs supplémentaires pour l'intelligence d'apprentissage.
    """
    email = models.EmailField(unique=True, verbose_name="Email", help_text="Adresse email unique de l'utilisateur")
    first_name = models.CharField(max_length=150, verbose_name="Prénom", help_text="Prénom de l'utilisateur")
    last_name = models.CharField(max_length=150, verbose_name="Nom", help_text="Nom de famille de l'utilisateur")

    # Contact fields
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Numéro de téléphone", help_text="Numéro de téléphone de l'utilisateur")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Pays", help_text="Pays de l'utilisateur")

    # Learning intelligence fields
    total_xp = models.IntegerField(default=0, verbose_name="XP Total", help_text="Points d'expérience cumulés (calculé automatiquement)")
    level = models.IntegerField(default=1, verbose_name="Niveau", help_text="Niveau actuel de l'utilisateur (calculé automatiquement)")

    # Currency system (DC - Decelcone)
    dc_balance = models.IntegerField(default=0, verbose_name="Solde DC", help_text="Solde en Decelcone (DC) - monnaie pour les achats sur le site")

    # Profile fields
    bio = models.TextField(blank=True, verbose_name="Biographie", help_text="Courte biographie de l'utilisateur")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar", help_text="Photo de profil de l'utilisateur")

    # Analytics fields
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dernière IP", help_text="Adresse IP de la dernière connexion")
    login_count = models.IntegerField(default=0, verbose_name="Nombre de connexions", help_text="Nombre total de connexions")
    current_streak = models.IntegerField(default=0, verbose_name="Série actuelle", help_text="Nombre de jours consécutifs d'activité")
    longest_streak = models.IntegerField(default=0, verbose_name="Plus longue série", help_text="Plus longue série de jours consécutifs")
    total_study_time_minutes = models.IntegerField(default=0, verbose_name="Temps d'étude total (minutes)", help_text="Temps total passé sur la plateforme")

    # Stripe
    stripe_customer_id = models.CharField(max_length=255, blank=True, verbose_name="ID client Stripe", help_text="ID client Stripe pour les paiements")

    # Streak Shield — protège le streak pour 1 jour
    streak_shield_active_until = models.DateField(null=True, blank=True, verbose_name="Streak Shield actif jusqu'au", help_text="Date jusqu'à laquelle le streak est protégé")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création", help_text="Date à laquelle le compte a été créé")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour", help_text="Dernière modification du profil")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_contributor(self):
        """Check if user is a contributor."""
        return hasattr(self, 'contributor') and self.contributor.is_active


class Contributor(models.Model):
    """
    Contributor model - users selected to create content.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contributor', verbose_name="Utilisateur")
    is_active = models.BooleanField(default=True, verbose_name="Actif", help_text="Cocher pour activer le contributeur")
    can_create_courses = models.BooleanField(default=True, verbose_name="Peut créer des cours", help_text="Autoriser la création de cours")
    can_create_exams = models.BooleanField(default=True, verbose_name="Peut créer des examens", help_text="Autoriser la création d'examens")
    can_create_community_content = models.BooleanField(default=True, verbose_name="Peut créer du contenu communautaire", help_text="Autoriser la création de contenu communautaire")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contributors', verbose_name="Créé par")

    # Plan d'abonnement
    PLAN_CHOICES = [
        ('free', 'Créateur Gratuit'),
        ('pro', 'Créateur Pro'),
        ('academy', 'Académie'),
    ]
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free', verbose_name="Plan")
    plan_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expiration du plan")
    stripe_subscription_id = models.CharField(max_length=255, blank=True, verbose_name="ID abonnement Stripe")
    total_content_sales = models.IntegerField(default=0, verbose_name="Total ventes contenu")
    total_dc_earned = models.IntegerField(default=0, verbose_name="Total DC gagnés")

    class Meta:
        verbose_name = "Contributeur"
        verbose_name_plural = "Contributeurs"

    @property
    def is_pro(self):
        """Retourne True si le contributeur a un plan actif (pro ou academy)."""
        from django.utils import timezone
        if self.plan == 'free':
            return False
        if self.plan_expires_at and self.plan_expires_at < timezone.now():
            return False
        return True

    def __str__(self):
        return f"{self.user.email} - {'Actif' if self.is_active else 'Inactif'}"


class DCTransaction(models.Model):
    """
    Model to track all DC (Decelcone) transactions - earnings and spendings.
    """
    TRANSACTION_TYPES = [
        ('purchase', 'Achat pack DC'),
        ('manual_payment', 'Paiement manuel validé'),
        ('recharge_code', 'Code de recharge'),
        ('sale', 'Vente'),
        ('exam_reward', 'Récompense examen'),
        ('daily_bonus', 'Bonus quotidien'),
        ('streak_shield', 'Streak Shield'),
        ('referral', 'Parrainage'),
        ('admin_grant', 'Octroi admin'),
        ('admin_deduct', 'Déduction admin'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dc_transactions', verbose_name="Utilisateur")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="Type de transaction")
    amount = models.IntegerField(verbose_name="Montant", help_text="Montant DC (positif pour gain, négatif pour dépense)")
    balance_after = models.IntegerField(verbose_name="Solde après transaction", help_text="Solde DC après cette transaction")
    description = models.TextField(blank=True, verbose_name="Description", help_text="Description de la transaction")
    related_content_type = models.CharField(max_length=50, blank=True, verbose_name="Type de contenu lié", help_text="Type de contenu si applicable (course, td, etc.)")
    related_content_id = models.IntegerField(blank=True, null=True, verbose_name="ID du contenu lié")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de transaction")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Transaction DC"
        verbose_name_plural = "Transactions DC"

    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.amount} DC - {self.created_at}"


class Referral(models.Model):
    """
    Modèle de parrainage - suit les parrainages entre utilisateurs.
    """
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made', verbose_name="Parrain")
    referred = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_received', null=True, blank=True, verbose_name="Filleul")
    referral_code = models.CharField(max_length=20, unique=True, verbose_name="Code de parrainage")
    reward_dc = models.IntegerField(default=50, verbose_name="Récompense DC", help_text="DC donnés au parrain quand le filleul s'inscrit")
    referred_reward_dc = models.IntegerField(default=25, verbose_name="Récompense filleul", help_text="DC donnés au filleul quand il s'inscrit")
    is_completed = models.BooleanField(default=False, verbose_name="Complété", help_text="True quand le filleul a complété les conditions")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de complétion")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Parrainage"
        verbose_name_plural = "Parrainages"
        unique_together = ['referrer', 'referred']

    def __str__(self):
        if self.referred:
            return f"{self.referrer.email} -> {self.referred.email} ({self.referral_code})"
        return f"{self.referrer.email} -> En attente ({self.referral_code})"


class PromoCode(models.Model):
    """
    Modèle de code promo - codes promotionnels pour les utilisateurs.
    """
    CODE_TYPES = [
        ('dc_bonus', 'Bonus DC'),
        ('xp_boost', 'Boost XP'),
        ('discount', 'Réduction'),
        ('special', 'Spécial'),
    ]

    code = models.CharField(max_length=30, unique=True, verbose_name="Code")
    code_type = models.CharField(max_length=20, choices=CODE_TYPES, verbose_name="Type de code")
    value = models.IntegerField(verbose_name="Valeur", help_text="Valeur du code (DC, %, etc.)")
    max_uses = models.IntegerField(null=True, blank=True, verbose_name="Utilisations max", help_text="Null pour illimité")
    used_count = models.IntegerField(default=0, verbose_name="Utilisations")
    valid_from = models.DateTimeField(verbose_name="Valide à partir de")
    valid_until = models.DateTimeField(verbose_name="Valide jusqu'à")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    description = models.TextField(blank=True, verbose_name="Description")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='promo_codes_created', verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Code Promo"
        verbose_name_plural = "Codes Promo"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.get_code_type_display()} ({self.value})"

    def is_valid(self):
        """Vérifie si le code promo est valide."""
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now:
            return False
        if self.valid_until < now:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True


class PromoCodeUsage(models.Model):
    """
    Modèle d'utilisation de code promo - suit qui a utilisé quels codes.
    """
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usages', verbose_name="Code promo")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promo_usages', verbose_name="Utilisateur")
    used_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'utilisation")
    reward_given = models.IntegerField(verbose_name="Récompense donnée", help_text="DC ou XP donnés")

    class Meta:
        verbose_name = "Utilisation de code promo"
        verbose_name_plural = "Utilisations de codes promo"
        unique_together = ['promo_code', 'user']

    def __str__(self):
        return f"{self.user.email} - {self.promo_code.code}"
