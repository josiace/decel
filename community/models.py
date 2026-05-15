from django.db import models
from django.conf import settings
from skills.models import Subject


# Types de contenu disponibles
CONTENT_FORMAT_CHOICES = [
    ('text', 'Texte brut'),
    ('pdf', 'Fichier PDF'),
    ('file', 'Autre fichier'),
]


class Content(models.Model):
    """
    Content model - community-submitted learning content.
    Workflow: DRAFT -> PENDING -> APPROVED/REJECTED
    """
    
    CONTENT_TYPES = [
        ('course', 'Cours'),
        ('td', 'TD (Travaux Dirigés)'),
        ('corrected_td', 'TD corrigé'),
    ]
    
    MODERATION_STATUS = [
        ('draft', 'Brouillon'),
        ('pending', 'En attente d\'approbation'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    # Content information
    title = models.CharField(max_length=255, verbose_name="Titre", help_text="Titre du contenu")
    description = models.TextField(blank=True, verbose_name="Description", help_text="Description courte du contenu")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, verbose_name="Type de contenu", help_text="Type de contenu soumis")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='community_content', verbose_name="Matière", help_text="Matière associée")
    
    # Content format
    content_format = models.CharField(max_length=20, choices=CONTENT_FORMAT_CHOICES, default='text', verbose_name="Format de contenu", help_text="Format du contenu (texte, PDF ou fichier)")
    
    # Content body (text)
    content = models.TextField(blank=True, verbose_name="Contenu texte", help_text="Contenu en texte ou HTML (si format = texte)")
    
    # Content file (PDF or other)
    content_file = models.FileField(upload_to='community/', null=True, blank=True, verbose_name="Fichier de contenu", help_text="Fichier PDF ou autre (si format = PDF ou fichier)")
    
    # Pricing
    xp_price = models.IntegerField(default=0, verbose_name="Prix en XP", help_text="XP requis pour accéder/télécharger ce contenu (0 = gratuit)")
    
    # Author and moderation
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_content', verbose_name="Auteur", help_text="Utilisateur qui a soumis le contenu")
    status = models.CharField(max_length=20, choices=MODERATION_STATUS, default='draft', verbose_name="Statut", help_text="Statut de modération du contenu")
    
    # Moderation
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_content',
        verbose_name="Modéré par",
        help_text="Modérateur qui a approuvé/rejeté le contenu"
    )
    moderation_notes = models.TextField(blank=True, verbose_name="Notes de modération", help_text="Notes du modérateur expliquant la décision")
    moderation_rule = models.ForeignKey(
        'ModerationRule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applied_content',
        verbose_name="Règle de modération",
        help_text="Règle appliquée lors de la modération"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    moderated_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de modération", help_text="Date à laquelle le contenu a été modéré")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contenu communautaire"
        verbose_name_plural = "Contenus communautaires"
    
    def __str__(self):
        return f"{self.title} ({self.status})"
    
    def can_edit(self, user):
        """Check if user can edit this content."""
        return user == self.author and self.status in ['draft', 'rejected']
    
    def can_moderate(self, user):
        """Check if user can moderate this content."""
        return user.is_staff or user.is_superuser


class ModerationRule(models.Model):
    """
    Modèle ModerationRule - règles pour la modération du contenu.
    Les administrateurs peuvent assigner des règles pour guider l'approbation du contenu.
    """
    name = models.CharField(max_length=255, unique=True, verbose_name="Nom", help_text="Nom unique de la règle")
    description = models.TextField(verbose_name="Description", help_text="Description de la règle")
    
    # Rule criteria
    required_word_count = models.IntegerField(null=True, blank=True, verbose_name="Nombre de mots minimum", help_text="Nombre minimum de mots requis")
    allowed_subjects = models.ManyToManyField(Subject, blank=True, verbose_name="Matières autorisées", help_text="Restreindre à des matières spécifiques")
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Créé par", help_text="Utilisateur qui a créé la règle")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    is_active = models.BooleanField(default=True, verbose_name="Actif", help_text="Cocher pour activer la règle")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Règle de modération"
        verbose_name_plural = "Règles de modération"
    
    def __str__(self):
        return self.name
