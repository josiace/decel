from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class BlogPost(models.Model):
    """Modèle pour les articles de blog."""
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]
    
    title = models.CharField(max_length=255, verbose_name="Titre")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Auteur")
    content = models.TextField(verbose_name="Contenu")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="Extrait")
    featured_image = models.ImageField(upload_to='blog/images/', blank=True, verbose_name="Image à la une")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    
    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta keywords")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de publication")
    
    # Analytics
    views_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    
    class Meta:
        ordering = ['-published_at']
        verbose_name = "Article de blog"
        verbose_name_plural = "Articles de blog"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})


class BlogCategory(models.Model):
    """Catégories pour les articles de blog."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Description")
    
    class Meta:
        verbose_name = "Catégorie de blog"
        verbose_name_plural = "Catégories de blog"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
