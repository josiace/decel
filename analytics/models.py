from django.db import models
from django.conf import settings


class UserActivity(models.Model):
    """
    UserActivity model - tracks all user activities for analytics.
    """
    ACTIVITY_TYPES = [
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('exam_start', 'Début examen'),
        ('exam_complete', 'Fin examen'),
        ('course_start', 'Début cours'),
        ('course_complete', 'Fin cours'),
        ('td_start', 'Début TD'),
        ('td_complete', 'Fin TD'),
        ('badge_earned', 'Badge obtenu'),
        ('level_up', 'Niveau supérieur'),
        ('recommendation_view', 'Vue recommandation'),
        ('leaderboard_view', 'Vue classement'),
        ('content_submit', 'Soumission contenu'),
        ('content_approved', 'Contenu approuvé'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities', verbose_name="Utilisateur")
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES, verbose_name="Type d'activité")
    
    # Related object IDs (optional)
    related_exam_id = models.IntegerField(null=True, blank=True, verbose_name="ID examen lié")
    related_course_id = models.IntegerField(null=True, blank=True, verbose_name="ID cours lié")
    related_td_id = models.IntegerField(null=True, blank=True, verbose_name="ID TD lié")
    related_badge_id = models.IntegerField(null=True, blank=True, verbose_name="ID badge lié")
    
    # Additional context (JSON)
    context = models.JSONField(default=dict, blank=True, verbose_name="Contexte", help_text="Données contextuelles supplémentaires")
    
    # Session tracking
    session_duration_seconds = models.IntegerField(null=True, blank=True, verbose_name="Durée session (secondes)", help_text="Durée de la session en secondes")
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'activité")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Activité utilisateur"
        verbose_name_plural = "Activités utilisateurs"
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()} - {self.created_at}"


class UserAnalytics(models.Model):
    """
    UserAnalytics model - stores computed analytics for users.
    Updated periodically via management command or signals.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics', verbose_name="Utilisateur")
    
    # Activity metrics
    total_activities = models.IntegerField(default=0, verbose_name="Total activités")
    activities_this_week = models.IntegerField(default=0, verbose_name="Activités cette semaine")
    activities_this_month = models.IntegerField(default=0, verbose_name="Activités ce mois")
    
    # Learning metrics
    total_exams_taken = models.IntegerField(default=0, verbose_name="Total examens passés")
    exams_passed = models.IntegerField(default=0, verbose_name="Examens réussis")
    exams_failed = models.IntegerField(default=0, verbose_name="Examens échoués")
    average_exam_score = models.IntegerField(null=True, blank=True, verbose_name="Score moyen examen")
    
    # Content metrics
    courses_completed = models.IntegerField(default=0, verbose_name="Cours complétés")
    tds_completed = models.IntegerField(default=0, verbose_name="TDs complétés")
    
    # Engagement metrics
    most_active_subject = models.ForeignKey('skills.Subject', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Matière la plus active")
    preferred_content_type = models.CharField(max_length=20, blank=True, verbose_name="Type de contenu préféré")
    
    # Time metrics
    total_time_spent_minutes = models.IntegerField(default=0, verbose_name="Temps total passé (minutes)")
    average_session_duration_minutes = models.IntegerField(null=True, blank=True, verbose_name="Durée moyenne session (minutes)")
    
    # Progress metrics
    skill_areas_improved = models.IntegerField(default=0, verbose_name="Zones de compétence améliorées")
    skill_areas_declined = models.IntegerField(default=0, verbose_name="Zones de compétence en déclin")
    
    # Metadata
    last_calculated_at = models.DateTimeField(auto_now=True, verbose_name="Dernier calcul")
    
    class Meta:
        verbose_name = "Analytics utilisateur"
        verbose_name_plural = "Analytics utilisateurs"
    
    def __str__(self):
        return f"Analytics - {self.user.email}"
