from django.db import models
from django.conf import settings


class Subject(models.Model):
    """
    Modèle de matière - représente un domaine d'apprentissage (ex: Mathématiques, Physique).
    Utilisé pour le suivi des compétences et le ciblage des recommandations.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom", help_text="Nom unique de la matière")
    description = models.TextField(blank=True, verbose_name="Description", help_text="Description détaillée de la matière")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icône", help_text="Nom de l'icône ou emoji")
    icon_image = models.ImageField(upload_to='subject_icons/', blank=True, null=True, verbose_name="Image de l'icône", help_text="Image personnalisée pour l'icône de la matière")
    use_image = models.BooleanField(default=False, verbose_name="Utiliser l'image", help_text="Cocher pour utiliser l'image au lieu de l'icône")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
    
    def __str__(self):
        return self.name


class UserSkill(models.Model):
    """
    Modèle UserSkill - suit les performances de l'utilisateur par matière.
    Implémente une pondération temporelle pour le calcul des compétences.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skills', verbose_name="Utilisateur", help_text="Utilisateur concerné")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='user_skills', verbose_name="Matière", help_text="Matière concernée")
    
    # Current skill level (0-100)
    skill_percentage = models.IntegerField(default=0, verbose_name="Pourcentage de compétence", help_text="Niveau de compétence en pourcentage (calculé automatiquement)")
    
    # Performance metrics
    total_exams_taken = models.IntegerField(default=0, verbose_name="Total d'examens passés", help_text="Nombre total d'examens passés dans cette matière")
    total_td_completed = models.IntegerField(default=0, verbose_name="Total de TD complétés", help_text="Nombre total de TD complétés dans cette matière")
    total_courses_read = models.IntegerField(default=0, verbose_name="Total de cours lus", help_text="Nombre total de cours lus dans cette matière")
    
    # Recency tracking
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Dernière activité", help_text="Date de la dernière activité dans cette matière")
    
    # Skill evolution tracking
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        unique_together = ['user', 'subject']
        ordering = ['-skill_percentage']
        verbose_name = "Compétence utilisateur"
        verbose_name_plural = "Compétences utilisateurs"
    
    def __str__(self):
        return f"{self.user.email} - {self.subject.name}: {self.skill_percentage}%"
