from django.contrib import admin
from .models import Course, TD, CorrectedTD, CourseProgress, TDProgress, ContentPurchase


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'content_type', 'xp_price', 'author', 'is_published', 'created_at']
    list_filter = ['subject', 'content_type', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    fieldsets = (
        ('Informations du cours', {'fields': ('title', 'description', 'subject'), 'description': 'Détails du cours'}),
        ('Type et format de contenu', {'fields': ('content_type', 'content', 'content_file'), 'description': 'Choisir le type de contenu et fournir soit le texte soit le fichier'}),
        ('Tarification', {'fields': ('xp_price',), 'description': 'Prix en XP pour accéder/télécharger (0 = gratuit)'}),
        ('Publication', {'fields': ('is_published',), 'description': 'Cocher pour rendre le cours visible'}),
        ('Métadonnées', {'fields': ('author', 'created_at', 'updated_at'), 'description': 'Informations de création'}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TD)
class TDAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'content_type', 'xp_price', 'author', 'is_published', 'created_at']
    list_filter = ['subject', 'content_type', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    fieldsets = (
        ('Informations du TD', {'fields': ('title', 'description', 'subject'), 'description': 'Détails du TD'}),
        ('Type et format de contenu', {'fields': ('content_type', 'content', 'content_file'), 'description': 'Choisir le type de contenu et fournir soit le texte soit le fichier'}),
        ('Tarification', {'fields': ('xp_price',), 'description': 'Prix en XP pour accéder/télécharger (0 = gratuit)'}),
        ('Publication', {'fields': ('is_published',), 'description': 'Cocher pour rendre le TD visible'}),
        ('Métadonnées', {'fields': ('author', 'created_at', 'updated_at'), 'description': 'Informations de création'}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CorrectedTD)
class CorrectedTDAdmin(admin.ModelAdmin):
    list_display = ['td', 'content_type', 'xp_price', 'created_at']
    list_filter = ['content_type', 'created_at']
    fieldsets = (
        ('Correction', {'fields': ('td', 'content_type', 'correction', 'correction_file'), 'description': 'TD associé et sa correction (texte ou fichier)'}),
        ('Tarification', {'fields': ('xp_price',), 'description': 'Prix en XP pour accéder/télécharger (0 = gratuit)'}),
        ('Horodatage', {'fields': ('created_at', 'updated_at'), 'description': 'Dates de création et de mise à jour'}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'is_completed', 'completed_at']
    list_filter = ['is_completed', 'completed_at']
    search_fields = ['user__email', 'course__title']
    fieldsets = (
        ('Progression', {'fields': ('user', 'course', 'is_completed'), 'description': 'Utilisateur et cours'}),
        ('Horodatage', {'fields': ('completed_at', 'created_at', 'updated_at'), 'description': 'Dates de progression'}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TDProgress)
class TDProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'td', 'is_completed', 'score', 'completed_at']
    list_filter = ['is_completed', 'completed_at']
    search_fields = ['user__email', 'td__title']
    fieldsets = (
        ('Progression', {'fields': ('user', 'td', 'is_completed', 'score'), 'description': 'Utilisateur et TD'}),
        ('Horodatage', {'fields': ('completed_at', 'created_at', 'updated_at'), 'description': 'Dates de progression'}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ContentPurchase)
class ContentPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'xp_paid', 'purchased_at']
    list_filter = ['content_type', 'purchased_at']
    search_fields = ['user__email']
    readonly_fields = ['purchased_at']
    fieldsets = (
        ('Achat', {'fields': ('user', 'content_type', 'course_id', 'td_id', 'corrected_td_id'), 'description': 'Détails de l\'achat'}),
        ('Paiement', {'fields': ('xp_paid',), 'description': 'XP payé pour le contenu'}),
        ('Horodatage', {'fields': ('purchased_at',), 'description': 'Date d\'achat'}),
    )
