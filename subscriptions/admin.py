from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, SubscriptionTransaction


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'billing_cycle', 'dc_price', 'is_active', 'is_popular', 'order']
    list_filter = ['plan_type', 'billing_cycle', 'is_active', 'is_popular']
    search_fields = ['name']
    list_editable = ['is_active', 'is_popular', 'order']
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'plan_type', 'billing_cycle')
        }),
        ('Pricing', {
            'fields': ('dc_price', 'stripe_price_id')
        }),
        ('Fonctionnalités', {
            'fields': ('features', 'max_courses_per_month', 'max_exams_per_month', 'max_tds_per_month')
        }),
        ('Fonctionnalités Premium', {
            'fields': ('has_certificates', 'has_mentoring', 'has_analytics', 'has_priority_support', 'has_ad_free')
        }),
        ('Métadonnées', {
            'fields': ('is_active', 'is_popular', 'order')
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew', 'days_remaining']
    list_filter = ['status', 'auto_renew', 'plan__plan_type']
    search_fields = ['user__email', 'plan__name']
    readonly_fields = ['days_remaining']
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'days_remaining')
        }),
        ('Paiement', {
            'fields': ('auto_renew', 'stripe_subscription_id', 'last_payment_date', 'next_payment_date')
        }),
        ('Annulation', {
            'fields': ('cancelled_at', 'cancellation_reason')
        }),
    )


@admin.register(SubscriptionTransaction)
class SubscriptionTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription', 'transaction_type', 'dc_amount', 'plan_name', 'created_at']
    list_filter = ['transaction_type', 'plan_type']
    search_fields = ['user__email', 'plan_name']
    readonly_fields = ['created_at']
