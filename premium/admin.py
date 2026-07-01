from django.contrib import admin
from .models import PremiumService, PremiumBooking, PremiumServiceReview


@admin.register(PremiumService)
class PremiumServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'provider', 'service_type', 'subject', 'dc_price_per_hour', 'status', 'created_at']
    list_filter = ['service_type', 'status', 'is_online', 'subject']
    search_fields = ['title', 'provider__email', 'description']
    fieldsets = (
        ('Informations de base', {
            'fields': ('provider', 'service_type', 'title', 'description', 'subject')
        }),
        ('Pricing', {
            'fields': ('dc_price_per_hour', 'dc_price_per_session')
        }),
        ('Disponibilité', {
            'fields': ('duration_minutes', 'is_online', 'location', 'max_students_per_session')
        }),
        ('Planning', {
            'fields': ('available_days', 'available_time_start', 'available_time_end')
        }),
        ('Statut', {
            'fields': ('status', 'requirements')
        }),
    )


@admin.register(PremiumBooking)
class PremiumBookingAdmin(admin.ModelAdmin):
    list_display = ['service', 'student', 'provider', 'scheduled_date', 'scheduled_time', 'status', 'dc_price', 'is_paid']
    list_filter = ['status', 'is_paid', 'service__service_type']
    search_fields = ['student__email', 'provider__email', 'service__title']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Informations de base', {
            'fields': ('service', 'student', 'provider')
        }),
        ('Planning', {
            'fields': ('scheduled_date', 'scheduled_time', 'duration_minutes')
        }),
        ('Paiement', {
            'fields': ('dc_price', 'is_paid')
        }),
        ('Statut', {
            'fields': ('status', 'meeting_link', 'meeting_notes')
        }),
        ('Annulation', {
            'fields': ('cancelled_at', 'cancellation_reason')
        }),
        ('Notation', {
            'fields': ('rating', 'review')
        }),
    )


@admin.register(PremiumServiceReview)
class PremiumServiceAdmin(admin.ModelAdmin):
    list_display = ['service', 'reviewer', 'rating', 'average_rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['reviewer__email', 'service__title']
    readonly_fields = ['average_rating', 'created_at']
