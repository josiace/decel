from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommendation_type', 'title', 'priority', 'is_active', 'is_dismissed', 'created_at']
    list_filter = ['recommendation_type', 'is_active', 'is_dismissed', 'priority', 'created_at']
    search_fields = ['user__email', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Recommandation', {'fields': ('user', 'recommendation_type', 'title', 'description'), 'description': 'Détails de la recommandation générée automatiquement'}),
        ('Contexte', {'fields': ('context',), 'description': 'Données contextuelles (JSON)'}),
        ('Priorité et statut', {'fields': ('priority', 'is_active', 'is_dismissed'), 'description': 'Priorité et statut de la recommandation'}),
        ('Contenu suggéré', {'fields': ('suggested_exam_id', 'suggested_course_id', 'suggested_td_id'), 'description': 'IDs du contenu suggéré (optionnel)'}),
        ('Horodatage', {'fields': ('created_at', 'updated_at'), 'description': 'Dates de création et de mise à jour'}),
    )
