from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from skills.models import Subject


# Types de contenu disponibles
CONTENT_TYPE_CHOICES = [
    ('text', 'Texte brut'),
    ('pdf', 'Fichier PDF'),
    ('image', 'Image'),
    ('file', 'Autre fichier'),
]


class ContentVersion(models.Model):
    """
    ContentVersion model - tracks version history for learning content.
    """
    CONTENT_TYPE_CHOICES = [
        ('course', 'Cours'),
        ('td', 'TD'),
        ('corrected_td', 'TD corrigé'),
    ]
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, verbose_name="Type de contenu")
    content_id = models.IntegerField(verbose_name="ID du contenu")
    
    # Version information
    version_number = models.IntegerField(verbose_name="Numéro de version")
    title = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Content snapshot
    content = models.TextField(blank=True, verbose_name="Contenu texte")
    content_file = models.FileField(upload_to='versions/', null=True, blank=True, verbose_name="Fichier de contenu")
    
    # Change log
    change_summary = models.TextField(verbose_name="Résumé des modifications", help_text="Description des changements dans cette version")
    
    # Author and metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        ordering = ['-version_number']
        verbose_name = "Version de contenu"
        verbose_name_plural = "Versions de contenu"
        unique_together = ['content_type', 'content_id', 'version_number']
    
    def __str__(self):
        return f"{self.get_content_type_display()} v{self.version_number} - {self.title}"


class Course(models.Model):
    """
    Modèle de cours - contenu éducatif pour l'apprentissage.
    La lecture d'un cours donne peu d'XP et met à jour l'engagement en compétences.
    """
    title = models.CharField(max_length=255, verbose_name="Titre", help_text="Titre du cours")
    description = models.TextField(blank=True, verbose_name="Description", help_text="Description courte du cours")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses', verbose_name="Matière", help_text="Matière associée au cours")
    
    # Course content type
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='text', verbose_name="Type de contenu", help_text="Type de contenu du cours")
    
    # Course content (text)
    content = models.TextField(blank=True, verbose_name="Contenu texte", help_text="Contenu du cours en texte ou HTML (si type = texte)")
    
    # Course file (PDF or other)
    content_file = models.FileField(upload_to='courses/', null=True, blank=True, verbose_name="Fichier de contenu", help_text="Fichier PDF ou autre (si type = PDF ou fichier)")
    
    # Pricing
    dc_price = models.IntegerField(default=0, verbose_name="Prix en DC", help_text="DC requis pour accéder/télécharger ce cours (0 = gratuit)")
    
    # Metadata
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Auteur", help_text="Auteur du cours")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    is_published = models.BooleanField(default=True, verbose_name="Publié", help_text="Cocher pour rendre le cours visible aux utilisateurs")
    
    # Versioning
    current_version = models.IntegerField(default=1, verbose_name="Version actuelle", help_text="Numéro de version actuel du cours")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
    
    def __str__(self):
        return self.title


class TD(models.Model):
    """
    Modèle de TD (Travaux Dirigés) - exercices pratiques.
    La complétion d'un TD donne un XP moyen et met à jour les compétences.
    """
    title = models.CharField(max_length=255, verbose_name="Titre", help_text="Titre du TD")
    description = models.TextField(blank=True, verbose_name="Description", help_text="Description courte du TD")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='tds', verbose_name="Matière", help_text="Matière associée au TD")
    
    # TD content type
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='text', verbose_name="Type de contenu", help_text="Type de contenu du TD")
    
    # TD content (text)
    content = models.TextField(blank=True, verbose_name="Contenu texte", help_text="Énoncé des exercices en texte ou HTML (si type = texte)")
    
    # TD file (PDF or other)
    content_file = models.FileField(upload_to='tds/', null=True, blank=True, verbose_name="Fichier de contenu", help_text="Fichier PDF ou autre (si type = PDF ou fichier)")
    
    # Pricing
    dc_price = models.IntegerField(default=0, verbose_name="Prix en DC", help_text="DC requis pour accéder/télécharger ce TD (0 = gratuit)")
    
    # Metadata
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Auteur", help_text="Auteur du TD")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    is_published = models.BooleanField(default=True, verbose_name="Publié", help_text="Cocher pour rendre le TD visible aux utilisateurs")
    
    # Versioning
    current_version = models.IntegerField(default=1, verbose_name="Version actuelle", help_text="Numéro de version actuel du TD")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "TD"
        verbose_name_plural = "TD"
    
    def __str__(self):
        return self.title


class CorrectedTD(models.Model):
    """
    Modèle de TD corrigé - TD avec solutions/corrections.
    Utilisé pour l'auto-apprentissage et la vérification.
    """
    td = models.OneToOneField(TD, on_delete=models.CASCADE, related_name='correction', verbose_name="TD", help_text="TD associé à cette correction")
    
    # Correction content type
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='text', verbose_name="Type de contenu", help_text="Type de contenu de la correction")
    
    # Correction content (text)
    correction = models.TextField(blank=True, verbose_name="Correction texte", help_text="Corrections détaillées et solutions des exercices (si type = texte)")
    
    # Correction file (PDF or other)
    correction_file = models.FileField(upload_to='corrections/', null=True, blank=True, verbose_name="Fichier de correction", help_text="Fichier PDF ou autre de la correction (si type = PDF ou fichier)")
    
    # Pricing
    dc_price = models.IntegerField(default=0, verbose_name="Prix en DC", help_text="DC requis pour accéder/télécharger cette correction (0 = gratuit)")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    # Versioning
    current_version = models.IntegerField(default=1, verbose_name="Version actuelle", help_text="Numéro de version actuel de la correction")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "TD corrigé"
        verbose_name_plural = "TD corrigés"
    
    def __str__(self):
        return f"Correction de {self.td.title}"


class CourseProgress(models.Model):
    """
    Modèle de progression de cours - suit la progression de l'utilisateur sur les cours.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_progress', verbose_name="Utilisateur", help_text="Utilisateur concerné")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progress', verbose_name="Cours", help_text="Cours concerné")
    
    # Progress tracking
    is_completed = models.BooleanField(default=False, verbose_name="Terminé", help_text="Indique si le cours a été terminé")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de complétion", help_text="Date à laquelle le cours a été terminé")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-updated_at']
        verbose_name = "Progression de cours"
        verbose_name_plural = "Progressions de cours"
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"


class TDProgress(models.Model):
    """
    Modèle de progression de TD - suit la progression de l'utilisateur sur les TD.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='td_progress', verbose_name="Utilisateur", help_text="Utilisateur concerné")
    td = models.ForeignKey(TD, on_delete=models.CASCADE, related_name='user_progress', verbose_name="TD", help_text="TD concerné")
    
    # Progress tracking
    is_completed = models.BooleanField(default=False, verbose_name="Terminé", help_text="Indique si le TD a été terminé")
    score = models.IntegerField(null=True, blank=True, verbose_name="Score", help_text="Score auto-déclaré (0-100)")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de complétion", help_text="Date à laquelle le TD a été terminé")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        unique_together = ['user', 'td']
        ordering = ['-updated_at']
        verbose_name = "Progression de TD"
        verbose_name_plural = "Progressions de TD"
    
    def __str__(self):
        return f"{self.user.email} - {self.td.title}"


class ContentPurchase(models.Model):
    """
    Modèle d'achat de contenu - suit les achats de contenu payant en XP.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='content_purchases', verbose_name="Utilisateur", help_text="Utilisateur qui a acheté le contenu")
    
    # Content type and ID (generic relation)
    content_type = models.CharField(max_length=20, choices=[('course', 'Cours'), ('td', 'TD'), ('corrected_td', 'TD corrigé')], verbose_name="Type de contenu", help_text="Type de contenu acheté")
    course_id = models.IntegerField(null=True, blank=True, verbose_name="ID cours", help_text="ID du cours acheté")
    td_id = models.IntegerField(null=True, blank=True, verbose_name="ID TD", help_text="ID du TD acheté")
    corrected_td_id = models.IntegerField(null=True, blank=True, verbose_name="ID TD corrigé", help_text="ID du TD corrigé acheté")
    
    # Purchase details
    dc_paid = models.IntegerField(verbose_name="DC payé", help_text="Quantité de DC payée")
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'achat", help_text="Date à laquelle le contenu a été acheté")
    
    class Meta:
        ordering = ['-purchased_at']
        verbose_name = "Achat de contenu"
        verbose_name_plural = "Achats de contenu"
    
    def __str__(self):
        return f"{self.user.email} - {self.content_type} - {self.dc_paid} DC"


class Review(models.Model):
    """
    Review model - user reviews and ratings for courses and TDs.
    """
    CONTENT_TYPES = [
        ('course', 'Cours'),
        ('td', 'TD'),
        ('corrected_td', 'TD corrigé'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name="Utilisateur")
    
    # Content being reviewed
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, verbose_name="Type de contenu")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews', verbose_name="Cours")
    td = models.ForeignKey('TD', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews', verbose_name="TD")
    corrected_td = models.ForeignKey('CorrectedTD', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews', verbose_name="TD corrigé")
    
    # Rating and review
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note",
        help_text="Note de 1 à 5 étoiles"
    )
    comment = models.TextField(blank=True, verbose_name="Commentaire", help_text="Commentaire détaillé")
    
    # Moderation
    is_approved = models.BooleanField(default=True, verbose_name="Approuvé", help_text="Indique si la review est visible")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        unique_together = ['user', 'content_type', 'course', 'td', 'corrected_td']
        ordering = ['-created_at']
        verbose_name = "Avis"
        verbose_name_plural = "Avis"

    def __str__(self):
        return f"{self.user.email} - {self.rating}/5"

    def get_content_title(self):
        """Get the title of the content being reviewed."""
        if self.content_type == 'course' and self.course:
            return self.course.title
        elif self.content_type == 'td' and self.td:
            return self.td.title
        elif self.content_type == 'corrected_td' and self.corrected_td:
            return self.corrected_td.title
        return "Contenu inconnu"

    def get_content_id(self):
        """Get the ID of the content being reviewed."""
        if self.content_type == 'course' and self.course:
            return self.course.id
        elif self.content_type == 'td' and self.td:
            return self.td.id
        elif self.content_type == 'corrected_td' and self.corrected_td:
            return self.corrected_td.id
        return None
