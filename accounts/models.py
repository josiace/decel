from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modèle d'utilisateur personnalisé pour DECEL.
    Étend le modèle AbstractUser de Django avec des champs supplémentaires pour l'intelligence d'apprentissage.
    """
    email = models.EmailField(unique=True, verbose_name="Email", help_text="Adresse email unique de l'utilisateur")
    first_name = models.CharField(max_length=150, verbose_name="Prénom", help_text="Prénom de l'utilisateur")
    last_name = models.CharField(max_length=150, verbose_name="Nom", help_text="Nom de famille de l'utilisateur")
    
    # Learning intelligence fields
    total_xp = models.IntegerField(default=0, verbose_name="XP Total", help_text="Points d'expérience cumulés (calculé automatiquement)")
    level = models.IntegerField(default=1, verbose_name="Niveau", help_text="Niveau actuel de l'utilisateur (calculé automatiquement)")
    
    # Profile fields
    bio = models.TextField(blank=True, verbose_name="Biographie", help_text="Courte biographie de l'utilisateur")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar", help_text="Photo de profil de l'utilisateur")
    
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
    
    class Meta:
        verbose_name = "Contributeur"
        verbose_name_plural = "Contributeurs"
    
    def __str__(self):
        return f"{self.user.email} - {'Actif' if self.is_active else 'Inactif'}"
