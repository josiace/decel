from django.contrib import admin
from .models import Subject, UserSkill


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']
    fieldsets = (
        ('Informations de la matière', {'fields': ('name', 'description', 'icon'), 'description': 'Détails de la matière d\'apprentissage'}),
        ('Horodatage', {'fields': ('created_at',), 'description': 'Date de création'}),
    )
    readonly_fields = ['created_at']


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'skill_percentage', 'total_exams_taken', 'total_td_completed', 'last_activity']
    list_filter = ['subject', 'skill_percentage', 'last_activity']
    search_fields = ['user__email', 'subject__name']
    readonly_fields = ['created_at', 'updated_at', 'last_activity']
    fieldsets = (
        ('Compétence', {'fields': ('user', 'subject', 'skill_percentage'), 'description': 'Niveau de compétence calculé automatiquement'}),
        ('Métriques de performance', {'fields': ('total_exams_taken', 'total_td_completed', 'total_courses_read'), 'description': 'Statistiques d\'activité dans cette matière'}),
        ('Activité', {'fields': ('last_activity',), 'description': 'Dernière activité dans cette matière'}),
        ('Horodatage', {'fields': ('created_at', 'updated_at'), 'description': 'Dates de création et de mise à jour'}),
    )
