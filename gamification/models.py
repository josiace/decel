from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Leaderboard(models.Model):
    """
    Leaderboard model - tracks rankings for different categories.
    """
    LEADERBOARD_TYPES = [
        ('global_xp', 'XP Global'),
        ('subject_skill', 'Compétence par Matière'),
        ('exams_passed', 'Examens Réussis'),
        ('badges_earned', 'Badges Obtenus'),
        ('streak', 'Série Consécutive'),
    ]
    
    name = models.CharField(max_length=255, unique=True, verbose_name="Nom", help_text="Nom du classement")
    leaderboard_type = models.CharField(max_length=20, choices=LEADERBOARD_TYPES, verbose_name="Type de classement", help_text="Type de classement")
    description = models.TextField(blank=True, verbose_name="Description", help_text="Description du classement")
    
    # For subject-specific leaderboards
    subject = models.ForeignKey(
        'skills.Subject',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='leaderboards',
        verbose_name="Matière",
        help_text="Matière concernée (pour les classements par compétence)"
    )
    
    # Time period
    TIME_PERIOD_CHOICES = [
        ('all_time', 'Tout le temps'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('yearly', 'Annuel'),
    ]
    time_period = models.CharField(max_length=20, choices=TIME_PERIOD_CHOICES, default='all_time', verbose_name="Période", help_text="Période du classement")
    
    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Actif", help_text="Cocher pour rendre le classement visible")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Classement"
        verbose_name_plural = "Classements"
    
    def __str__(self):
        return self.name


class LeaderboardEntry(models.Model):
    """
    LeaderboardEntry model - stores user positions in leaderboards.
    Updated periodically via management command or signal.
    """
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name='entries', verbose_name="Classement")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leaderboard_entries', verbose_name="Utilisateur")
    
    # Position and score
    position = models.IntegerField(verbose_name="Position", help_text="Position dans le classement")
    score = models.IntegerField(default=0, verbose_name="Score", help_text="Score de l'utilisateur")
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        unique_together = ['leaderboard', 'user']
        ordering = ['position']
        verbose_name = "Entrée de classement"
        verbose_name_plural = "Entrées de classement"
    
    def __str__(self):
        return f"{self.leaderboard.name} - {self.user.email} - Position {self.position}"


class XPLog(models.Model):
    """
    Modèle XPLog - suit les XP attribués aux utilisateurs.
    L'XP est pour le suivi de progression, pas une monnaie.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='xp_logs', verbose_name="Utilisateur", help_text="Utilisateur concerné")
    
    # XP amount awarded
    amount = models.IntegerField(verbose_name="Montant XP", help_text="Quantité d'XP attribuée")
    
    # Reason for awarding XP
    reason = models.CharField(max_length=255, verbose_name="Raison", help_text="Raison de l'attribution de l'XP")
    
    # Action type (exam, td, course, etc.)
    action_type = models.CharField(max_length=50, verbose_name="Type d'action", help_text="Type d'action qui a gagné de l'XP (exam, td, course, etc.)")
    
    # Related object IDs (optional, for tracking)
    related_exam_id = models.IntegerField(null=True, blank=True, verbose_name="ID examen lié", help_text="ID de l'examen associé (si applicable)")
    related_td_id = models.IntegerField(null=True, blank=True, verbose_name="ID TD lié", help_text="ID du TD associé (si applicable)")
    related_course_id = models.IntegerField(null=True, blank=True, verbose_name="ID cours lié", help_text="ID du cours associé (si applicable)")
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'attribution")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Journal XP"
        verbose_name_plural = "Journaux XP"
    
    def __str__(self):
        return f"{self.user.email} +{self.amount} XP ({self.action_type})"


class Badge(models.Model):
    """
    Modèle Badge - réalisations qui peuvent être gagnées.
    Les badges sont attribués en fonction des accomplissements.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom", help_text="Nom unique du badge")
    description = models.TextField(verbose_name="Description", help_text="Description du badge")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icône", help_text="Nom de l'icône ou emoji")
    
    # Badge criteria
    xp_threshold = models.IntegerField(null=True, blank=True, verbose_name="Seuil XP", help_text="XP requis pour obtenir ce badge")
    exam_count_threshold = models.IntegerField(null=True, blank=True, verbose_name="Seuil nombre d'examens", help_text="Nombre d'examens requis")
    skill_threshold = models.IntegerField(null=True, blank=True, verbose_name="Seuil compétence", help_text="Pourcentage de compétence requis")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    is_active = models.BooleanField(default=True, verbose_name="Actif", help_text="Cocher pour rendre le badge disponible")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
    
    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """
    Modèle UserBadge - suit les badges gagnés par les utilisateurs.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges', verbose_name="Utilisateur", help_text="Utilisateur concerné")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges', verbose_name="Badge", help_text="Badge obtenu")
    
    # When the badge was earned
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'obtention", help_text="Date à laquelle le badge a été obtenu")
    
    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
        verbose_name = "Badge utilisateur"
        verbose_name_plural = "Badges utilisateurs"
    
    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"
