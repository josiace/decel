from django.contrib import admin
from .models import Content, ModerationRule


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'content_format', 'xp_price', 'subject', 'author', 'status', 'created_at']
    list_filter = ['content_type', 'content_format', 'status', 'subject', 'created_at']
    search_fields = ['title', 'description', 'author__email']
    readonly_fields = ['created_at', 'updated_at', 'moderated_at']
    fieldsets = (
        ('Contenu', {'fields': ('title', 'description', 'content_type', 'subject'), 'description': 'Informations du contenu soumis'}),
        ('Format de contenu', {'fields': ('content_format', 'content', 'content_file'), 'description': 'Choisir le format et fournir soit le texte soit le fichier'}),
        ('Tarification', {'fields': ('xp_price',), 'description': 'Prix en XP pour accéder/télécharger (0 = gratuit)'}),
        ('Auteur et statut', {'fields': ('author', 'status'), 'description': 'Auteur et statut de modération'}),
        ('Modération', {'fields': ('moderated_by', 'moderation_notes', 'moderation_rule'), 'description': 'Détails de la modération'}),
        ('Horodatage', {'fields': ('created_at', 'updated_at', 'moderated_at'), 'description': 'Dates de création et de modération'}),
    )


@admin.register(ModerationRule)
class ModerationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'required_word_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['allowed_subjects']
    fieldsets = (
        ('Règle', {'fields': ('name', 'description'), 'description': 'Nom et description de la règle'}),
        ('Critères', {'fields': ('required_word_count', 'allowed_subjects'), 'description': 'Critères de validation du contenu'}),
        ('Publication', {'fields': ('is_active',), 'description': 'Cocher pour activer la règle'}),
        ('Métadonnées', {'fields': ('created_by', 'created_at'), 'description': 'Informations de création'}),
    )
    readonly_fields = ['created_at']
