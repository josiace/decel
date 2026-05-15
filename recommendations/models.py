from django.db import models
from django.conf import settings


class Recommendation(models.Model):
    """
    Recommendation model - adaptive learning suggestions.
    Generated dynamically based on user performance and skills.
    """
    
    # Recommendation types
    RECOMMENDATION_TYPES = [
        ('review', 'Réviser - Suggérer la révision pour les domaines faibles'),
        ('advance', 'Avancer - Suggérer du contenu plus difficile pour les domaines forts'),
        ('practice', 'Pratiquer - Suggérer des TD pour l\'amélioration des compétences'),
        ('learn', 'Apprendre - Suggérer des cours pour de nouveaux sujets'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations', verbose_name="Utilisateur", help_text="Utilisateur concerné")
    
    # Recommendation type
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES, verbose_name="Type de recommandation", help_text="Type de recommandation généré")
    
    # Recommendation content
    title = models.CharField(max_length=255, verbose_name="Titre", help_text="Titre de la recommandation")
    description = models.TextField(verbose_name="Description", help_text="Description détaillée de la recommandation")
    
    # Context (JSON) - stores relevant data like subject, score, etc.
    context = models.JSONField(default=dict, blank=True, verbose_name="Contexte", help_text="Données contextuelles (JSON) comme matière, score, etc.")
    
    # Priority (higher = more important)
    priority = models.IntegerField(default=5, verbose_name="Priorité", help_text="1-10, plus élevé = plus important")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Actif", help_text="Indique si la recommandation est active")
    is_dismissed = models.BooleanField(default=False, verbose_name="Ignoré", help_text="Indique si l'utilisateur a ignoré la recommandation")
    
    # Related content (optional)
    suggested_exam_id = models.IntegerField(null=True, blank=True, verbose_name="ID examen suggéré", help_text="ID de l'examen suggéré (si applicable)")
    suggested_course_id = models.IntegerField(null=True, blank=True, verbose_name="ID cours suggéré", help_text="ID du cours suggéré (si applicable)")
    suggested_td_id = models.IntegerField(null=True, blank=True, verbose_name="ID TD suggéré", help_text="ID du TD suggéré (si applicable)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = "Recommandation"
        verbose_name_plural = "Recommandations"
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
