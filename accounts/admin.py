from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Contributor


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'total_xp', 'level', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'level']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Intelligence d\'Apprentissage', {'fields': ('total_xp', 'level'), 'description': 'Points d\'expérience et niveau calculés automatiquement'}),
        ('Profil', {'fields': ('bio', 'avatar'), 'description': 'Informations du profil utilisateur'}),
        ('Horodatage', {'fields': ('created_at', 'updated_at'), 'description': 'Dates de création et de mise à jour'}),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        perms['view'] = True
        return perms


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'can_create_courses', 'can_create_exams', 'can_create_community_content', 'created_at']
    list_filter = ['is_active', 'can_create_courses', 'can_create_exams', 'can_create_community_content', 'created_at']
    search_fields = ['user__email', 'user__username', 'user__first_name', 'user__last_name']
    fieldsets = (
        ('Contributeur', {'fields': ('user', 'is_active'), 'description': 'Utilisateur et statut du contributeur'}),
        ('Permissions', {'fields': ('can_create_courses', 'can_create_exams', 'can_create_community_content'), 'description': 'Permissions du contributeur'}),
        ('Métadonnées', {'fields': ('created_at', 'created_by'), 'description': 'Informations de création'}),
    )
    readonly_fields = ['created_at']
