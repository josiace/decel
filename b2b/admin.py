from django.contrib import admin
from .models import B2BPartner, B2BLicense, B2BUser, B2BTransaction


@admin.register(B2BPartner)
class B2BPartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner_type', 'contact_person', 'email', 'status', 'created_at']
    list_filter = ['partner_type', 'status']
    search_fields = ['name', 'contact_person', 'email']
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'partner_type', 'status')
        }),
        ('Contact', {
            'fields': ('contact_person', 'email', 'phone', 'address')
        }),
        ('Organisation', {
            'fields': ('tax_id', 'registration_number')
        }),
        ('Contrat', {
            'fields': ('contract_start_date', 'contract_end_date', 'contract_terms')
        }),
        ('Facturation', {
            'fields': ('billing_email', 'billing_address')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(B2BLicense)
class B2BLicenseAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner', 'license_type', 'license_key', 'max_students', 'current_students', 'status', 'is_active', 'days_remaining']
    list_filter = ['license_type', 'status', 'has_certificates', 'has_analytics', 'has_api_access']
    search_fields = ['name', 'partner__name', 'license_key']
    readonly_fields = ['license_key', 'is_active', 'days_remaining', 'usage_percentage']
    fieldsets = (
        ('Informations de base', {
            'fields': ('partner', 'license_type', 'name', 'description', 'license_key')
        }),
        ('Pricing', {
            'fields': ('price_cfa', 'billing_cycle')
        }),
        ('Limites', {
            'fields': ('max_students', 'current_students', 'max_teachers', 'current_teachers', 'max_courses', 'max_exams')
        }),
        ('Fonctionnalités', {
            'fields': ('has_certificates', 'has_analytics', 'has_api_access', 'has_custom_branding', 'has_priority_support')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'is_active', 'days_remaining')
        }),
        ('Utilisation', {
            'fields': ('usage_percentage',)
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(B2BUser)
class B2BUserAdmin(admin.ModelAdmin):
    list_display = ['license', 'user', 'role', 'added_at', 'added_by']
    list_filter = ['role']
    search_fields = ['user__email', 'license__name']
    readonly_fields = ['added_at']


@admin.register(B2BTransaction)
class B2BTransactionAdmin(admin.ModelAdmin):
    list_display = ['partner', 'license', 'transaction_type', 'amount_cfa', 'status', 'created_at']
    list_filter = ['transaction_type', 'status']
    search_fields = ['partner__name', 'invoice_number', 'payment_reference']
    readonly_fields = ['created_at', 'completed_at']
    fieldsets = (
        ('Informations de base', {
            'fields': ('partner', 'license', 'transaction_type', 'amount_cfa')
        }),
        ('Paiement', {
            'fields': ('payment_method', 'payment_reference')
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Facture', {
            'fields': ('invoice_number', 'invoice_sent')
        }),
        ('Dates', {
            'fields': ('created_at', 'completed_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
