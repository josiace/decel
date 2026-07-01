from django.db import models
from django.conf import settings


class PageView(models.Model):
    """
    PageView model - tracks every page view for analytics.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='page_views', verbose_name="Utilisateur")
    session_id = models.CharField(max_length=255, db_index=True, verbose_name="ID Session")
    url = models.CharField(max_length=500, verbose_name="URL")
    page_title = models.CharField(max_length=255, blank=True, verbose_name="Titre de la page")
    referrer = models.URLField(blank=True, verbose_name="Référant")
    duration_seconds = models.IntegerField(null=True, blank=True, verbose_name="Durée (secondes)")

    # Device info
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    device_type = models.CharField(max_length=50, blank=True, verbose_name="Type d'appareil")
    browser = models.CharField(max_length=50, blank=True, verbose_name="Navigateur")
    os = models.CharField(max_length=50, blank=True, verbose_name="Système d'exploitation")

    # Location info (optional, from IP)
    country = models.CharField(max_length=100, blank=True, verbose_name="Pays")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de la vue")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Vue de page"
        verbose_name_plural = "Vues de pages"
        indexes = [
            models.Index(fields=['session_id', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['url']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else "Anonyme"
        return f"{user_str} - {self.url} - {self.created_at}"


class ClickEvent(models.Model):
    """
    ClickEvent model - tracks click events on the site.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='click_events', verbose_name="Utilisateur")
    session_id = models.CharField(max_length=255, db_index=True, verbose_name="ID Session")
    page_url = models.CharField(max_length=500, verbose_name="URL de la page")

    # Click target info
    element_id = models.CharField(max_length=255, blank=True, verbose_name="ID de l'élément")
    element_class = models.CharField(max_length=255, blank=True, verbose_name="Classe de l'élément")
    element_tag = models.CharField(max_length=50, blank=True, verbose_name="Tag de l'élément")
    element_text = models.CharField(max_length=255, blank=True, verbose_name="Texte de l'élément")
    href = models.URLField(blank=True, verbose_name="Lien (href)")

    # Click position
    x_position = models.IntegerField(null=True, blank=True, verbose_name="Position X")
    y_position = models.IntegerField(null=True, blank=True, verbose_name="Position Y")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date du clic")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Événement de clic"
        verbose_name_plural = "Événements de clics"
        indexes = [
            models.Index(fields=['session_id', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['page_url']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else "Anonyme"
        return f"{user_str} - {self.element_text or self.element_id} - {self.page_url}"


class UserSession(models.Model):
    """
    UserSession model - tracks complete user sessions/journeys.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions', verbose_name="Utilisateur")
    session_id = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="ID Session")

    # Session metrics
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Heure de début")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Heure de fin")
    duration_seconds = models.IntegerField(null=True, blank=True, verbose_name="Durée (secondes)")

    # Page counts
    page_views_count = models.IntegerField(default=0, verbose_name="Nombre de vues")
    unique_pages_count = models.IntegerField(default=0, verbose_name="Pages uniques")

    # Entry and exit
    entry_page = models.CharField(max_length=500, blank=True, verbose_name="Page d'entrée")
    exit_page = models.CharField(max_length=500, blank=True, verbose_name="Page de sortie")

    # Device info
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    device_type = models.CharField(max_length=50, blank=True, verbose_name="Type d'appareil")

    # Location
    country = models.CharField(max_length=100, blank=True, verbose_name="Pays")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")

    # Journey path (ordered list of pages visited)
    journey_path = models.JSONField(default=list, blank=True, verbose_name="Parcours")

    # Metadata
    is_completed = models.BooleanField(default=False, verbose_name="Session terminée")

    class Meta:
        ordering = ['-start_time']
        verbose_name = "Session utilisateur"
        verbose_name_plural = "Sessions utilisateurs"
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', '-start_time']),
            models.Index(fields=['-start_time']),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else "Anonyme"
        return f"{user_str} - {self.session_id} - {self.start_time}"


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
