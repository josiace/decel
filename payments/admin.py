from django.contrib import admin
from django.contrib import messages
from .models import DCPack, DCPackOrder, RechargeCode
from .services import ManualPaymentService, MANUAL_PAYMENT_METHODS, DCPackOrderService


@admin.register(DCPack)
class DCPackAdmin(admin.ModelAdmin):
    list_display = ['name', 'dc_amount', 'price_cfa', 'dc_per_cfa', 'is_popular', 'is_active', 'order']
    list_editable = ['is_popular', 'is_active', 'order']
    list_filter = ['is_active', 'is_popular']
    search_fields = ['name']
    readonly_fields = ['created_at']

    def dc_per_cfa(self, obj):
        return f"{obj.dc_per_cfa} DC/FCFA"
    dc_per_cfa.short_description = "Valeur"


@admin.register(DCPackOrder)
class DCPackOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'pack', 'dc_amount', 'price_paid_cfa', 'payment_method', 'status', 'dc_credited', 'created_at', 'completed_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__email', 'stripe_session_id', 'stripe_payment_intent', 'transaction_reference']
    readonly_fields = ['user', 'pack', 'dc_amount', 'price_paid_cfa', 'stripe_session_id',
                       'stripe_payment_intent', 'created_at', 'completed_at']
    fieldsets = (
        ('Commande', {'fields': ('user', 'pack', 'dc_amount', 'price_paid_cfa'), 'description': 'Détails de la commande'}),
        ('Paiement', {'fields': ('payment_method', 'stripe_session_id', 'stripe_payment_intent', 'transaction_reference'), 'description': 'Informations de paiement'}),
        ('Validation', {'fields': ('status', 'admin_notes'), 'description': 'Passer le statut à « Complété » crédite automatiquement les DC. Vous pouvez aussi utiliser l\'action « Valider les paiements » dans le menu déroulant.'}),
        ('Horodatage', {'fields': ('created_at', 'completed_at'), 'description': 'Dates'}),
    )
    ordering = ['-created_at']
    actions = ['validate_payments', 'reject_payments', 'recredit_missing_dc']

    @admin.display(boolean=True, description='DC crédités')
    def dc_credited(self, obj):
        return DCPackOrderService.has_dc_credit(obj)

    def save_model(self, request, obj, form, change):
        """
        Crédite les DC si l'admin passe une commande manuelle à « Complété »
        depuis le formulaire (sans passer par l'action du menu déroulant).
        """
        if change and obj.payment_method in MANUAL_PAYMENT_METHODS:
            previous = DCPackOrder.objects.filter(pk=obj.pk).first()
            if previous and previous.status != 'completed' and obj.status == 'completed':
                success, message = ManualPaymentService.validate_manual_payment(
                    obj.id,
                    admin_notes=obj.admin_notes or '',
                )
                if success:
                    obj.refresh_from_db()
                    messages.success(request, message)
                else:
                    obj.status = previous.status
                    messages.error(request, message)

        super().save_model(request, obj, form, change)

    def validate_payments(self, request, queryset):
        """Action admin pour valider les paiements manuels."""
        validated_count = 0
        for order in queryset.filter(status='pending', payment_method__in=MANUAL_PAYMENT_METHODS):
            try:
                success, message = ManualPaymentService.validate_manual_payment(order.id)
                
                if success:
                    validated_count += 1
                    # Rafraîchir l'objet pour voir le nouveau solde
                    order.user.refresh_from_db()
                    self.message_user(request, f"Commande #{order.id} validée. Nouveau solde de {order.user.email}: {order.user.dc_balance} DC", messages.INFO)
                else:
                    self.message_user(request, f"Erreur pour la commande #{order.id}: {message}", messages.ERROR)
            except Exception as e:
                self.message_user(request, f"Exception pour la commande #{order.id}: {str(e)}", messages.ERROR)
        
        if validated_count > 0:
            self.message_user(request, f"{validated_count} paiement(s) validé(s) avec succès. Les DC ont été crédités aux utilisateurs.", messages.SUCCESS)
        else:
            self.message_user(request, "Aucun paiement n'a été validé. Vérifiez que les commandes sont en statut 'pending' et utilisent une méthode de paiement manuelle.", messages.WARNING)
    
    validate_payments.short_description = "✓ Valider les paiements (créditer DC immédiatement)"

    def reject_payments(self, request, queryset):
        """Action admin pour rejeter les paiements manuels."""
        rejected_count = 0
        for order in queryset.filter(status='pending', payment_method__in=MANUAL_PAYMENT_METHODS):
            success, message = ManualPaymentService.reject_manual_payment(order.id)
            if success:
                rejected_count += 1
            else:
                self.message_user(request, f"Erreur pour la commande #{order.id}: {message}", messages.ERROR)
        
        if rejected_count > 0:
            self.message_user(request, f"{rejected_count} paiement(s) rejeté(s).", messages.SUCCESS)
        else:
            self.message_user(request, "Aucun paiement n'a été rejeté.", messages.WARNING)
    
    reject_payments.short_description = "✗ Rejeter les paiements"

    def recredit_missing_dc(self, request, queryset):
        """Recrédite les commandes complétées sans transaction DC."""
        recredited_count = 0
        for order in queryset.filter(status='completed'):
            if DCPackOrderService.has_dc_credit(order):
                continue
            try:
                success, message = DCPackOrderService.recredit_missing_order(
                    order,
                    admin_notes=f"Recrédit admin par {request.user.email}",
                )
                if success:
                    recredited_count += 1
                    order.user.refresh_from_db()
                    self.message_user(
                        request,
                        f"Commande #{order.id} : {message}",
                        messages.SUCCESS,
                    )
                else:
                    self.message_user(
                        request,
                        f"Commande #{order.id} : {message}",
                        messages.WARNING,
                    )
            except Exception as e:
                self.message_user(
                    request,
                    f"Exception commande #{order.id} : {e}",
                    messages.ERROR,
                )

        if recredited_count == 0:
            self.message_user(
                request,
                "Aucune commande recréditée. Sélectionnez des commandes « Complétées » sans DC crédités.",
                messages.WARNING,
            )

    recredit_missing_dc.short_description = "↺ Recréditer les DC manquants (commandes complétées sans crédit)"


@admin.register(RechargeCode)
class RechargeCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'dc_amount', 'status', 'created_by', 'used_by', 'used_at', 'expires_at', 'created_at']
    list_filter = ['status', 'created_at', 'expires_at']
    search_fields = ['code', 'created_by__email', 'used_by__email']
    readonly_fields = ['created_at', 'used_at']
    fieldsets = (
        ('Code', {'fields': ('code', 'dc_amount', 'status'), 'description': 'Informations du code'}),
        ('Utilisation', {'fields': ('created_by', 'used_by', 'used_at'), 'description': 'Qui a créé/utilisé le code'}),
        ('Validité', {'fields': ('expires_at',), 'description': 'Date d\'expiration'}),
        ('Notes', {'fields': ('notes',), 'description': 'Notes additionnelles'}),
        ('Horodatage', {'fields': ('created_at',), 'description': 'Date de création'}),
    )
    ordering = ['-created_at']
