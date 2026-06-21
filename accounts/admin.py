from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import User, Contributor, Country, DCTransaction, Referral, PromoCode, PromoCodeUsage


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    fieldsets = (
        ('Pays', {'fields': ('name', 'code', 'is_active'), 'description': 'Informations du pays'}),
        ('Métadonnées', {'fields': ('created_at',), 'description': 'Date de création'}),
    )
    readonly_fields = ['created_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'country', 'total_xp', 'level', 'dc_balance', 'is_staff', 'created_at', 'view_user_analytics', 'view_user_details']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'level', 'country', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Contact', {'fields': ('phone_number', 'country'), 'description': 'Informations de contact'}),
        ('Intelligence d\'Apprentissage', {'fields': ('total_xp', 'level'), 'description': 'Points d\'expérience et niveau calculés automatiquement'}),
        ('Monnaie DC', {'fields': ('dc_balance',), 'description': 'Solde en Decelcone (DC) pour les achats sur le site'}),
        ('Profil', {'fields': ('bio', 'avatar'), 'description': 'Informations du profil utilisateur'}),
        ('Analytics', {'fields': ('last_login_ip', 'login_count', 'current_streak', 'longest_streak', 'total_study_time_minutes'), 'description': 'Données analytiques de l\'utilisateur'}),
        ('Horodatage', {'fields': ('created_at', 'updated_at'), 'description': 'Dates de création et de mise à jour'}),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_login_ip']

    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        perms['view'] = True
        return perms

    def view_user_analytics(self, obj):
        url = reverse('analytics:admin_user_analytics', args=[obj.id])
        return format_html('<a href="{}" class="button" style="background-color: #4CAF50; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">📊 Graphiques</a>', url)
    view_user_analytics.short_description = 'Analytiques'

    def view_user_details(self, obj):
        url = reverse('admin_user_detail', args=[obj.id])
        return format_html('<a href="{}" class="button">Voir détails</a>', url)
    view_user_details.short_description = 'Détails'


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


@admin.register(DCTransaction)
class DCTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__email', 'description']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Transaction', {'fields': ('user', 'transaction_type', 'amount', 'balance_after'), 'description': 'Détails de la transaction'}),
        ('Description', {'fields': ('description', 'related_content_type', 'related_content_id'), 'description': 'Informations supplémentaires'}),
        ('Horodatage', {'fields': ('created_at',), 'description': 'Date de transaction'}),
    )


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred', 'referral_code', 'reward_dc', 'referred_reward_dc', 'is_completed', 'completed_at', 'created_at']
    list_filter = ['is_completed', 'created_at']
    search_fields = ['referrer__email', 'referred__email', 'referral_code']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Parrainage', {'fields': ('referrer', 'referred', 'referral_code'), 'description': 'Relation parrain-filleul'}),
        ('Récompenses', {'fields': ('reward_dc', 'referred_reward_dc'), 'description': 'Montants DC distribués'}),
        ('Statut', {'fields': ('is_completed', 'completed_at'), 'description': 'État du parrainage'}),
        ('Horodatage', {'fields': ('created_at',), 'description': 'Date de création'}),
    )


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'code_type', 'value', 'max_uses', 'used_count', 'is_active', 'valid_from', 'valid_until', 'created_at']
    list_filter = ['code_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'description']
    readonly_fields = ['used_count', 'created_at']
    fieldsets = (
        ('Code Promo', {'fields': ('code', 'code_type', 'value'), 'description': 'Informations du code'}),
        ('Limitations', {'fields': ('max_uses', 'used_count', 'is_active'), 'description': 'Utilisations et statut'}),
        ('Validité', {'fields': ('valid_from', 'valid_until'), 'description': 'Période de validité'}),
        ('Description', {'fields': ('description',), 'description': 'Description du code'}),
        ('Création', {'fields': ('created_by', 'created_at'), 'description': 'Informations de création'}),
    )


@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ['user', 'promo_code', 'reward_given', 'used_at']
    list_filter = ['used_at', 'promo_code__code_type']
    search_fields = ['user__email', 'promo_code__code']
    readonly_fields = ['used_at']
    fieldsets = (
        ('Utilisation', {'fields': ('user', 'promo_code', 'reward_given'), 'description': 'Détails de l\'utilisation'}),
        ('Horodatage', {'fields': ('used_at',), 'description': 'Date d\'utilisation'}),
    )
