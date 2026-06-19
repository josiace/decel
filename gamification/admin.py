from django.contrib import admin
from .models import XPLog, Badge, UserBadge, Leaderboard, LeaderboardEntry


@admin.register(XPLog)
class XPLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'action_type', 'reason', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__email', 'reason']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Gain d\'XP', {'fields': ('user', 'amount', 'reason', 'action_type'), 'description': 'Détails du gain d\'XP'}),
        ('Objets liés', {'fields': ('related_exam_id', 'related_td_id', 'related_course_id'), 'description': 'IDs des objets associés (optionnel)'}),
        ('Horodatage', {'fields': ('created_at',), 'description': 'Date d\'attribution'}),
    )


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'xp_threshold', 'exam_count_threshold', 'skill_threshold', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Badge', {'fields': ('name', 'description', 'icon'), 'description': 'Informations du badge'}),
        ('Critères d\'obtention', {'fields': ('xp_threshold', 'exam_count_threshold', 'skill_threshold'), 'description': 'Seuils requis pour obtenir le badge'}),
        ('Publication', {'fields': ('is_active',), 'description': 'Cocher pour rendre le badge disponible'}),
        ('Horodatage', {'fields': ('created_at',), 'description': 'Date de création'}),
    )
    readonly_fields = ['created_at']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']
    list_filter = ['badge', 'earned_at']
    search_fields = ['user__email', 'badge__name']
    readonly_fields = ['earned_at']
    fieldsets = (
        ('Badge utilisateur', {'fields': ('user', 'badge'), 'description': 'Utilisateur et badge obtenu'}),
        ('Horodatage', {'fields': ('earned_at',), 'description': 'Date d\'obtention'}),
    )


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'leaderboard_type', 'subject', 'time_period', 'is_active', 'created_at']
    list_filter = ['leaderboard_type', 'time_period', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Classement', {'fields': ('name', 'description', 'leaderboard_type'), 'description': 'Informations du classement'}),
        ('Configuration', {'fields': ('subject', 'time_period'), 'description': 'Matière et période du classement'}),
        ('Publication', {'fields': ('is_active',), 'description': 'Cocher pour rendre le classement visible'}),
        ('Horodatage', {'fields': ('created_at', 'updated_at'), 'description': 'Dates de création et de mise à jour'}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ['leaderboard', 'user', 'position', 'score', 'updated_at']
    list_filter = ['leaderboard', 'position', 'updated_at']
    search_fields = ['user__email', 'leaderboard__name']
    fieldsets = (
        ('Entrée de classement', {'fields': ('leaderboard', 'user'), 'description': 'Classement et utilisateur'}),
        ('Performance', {'fields': ('position', 'score'), 'description': 'Position et score de l\'utilisateur'}),
        ('Horodatage', {'fields': ('updated_at',), 'description': 'Date de mise à jour'}),
    )
    readonly_fields = ['updated_at']
