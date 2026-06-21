"""
Services pour la gestion des paiements alternatifs (sans API).
Gère les codes de recharge et la validation manuelle des paiements.
"""
import random
import string
from django.db import transaction
from django.utils import timezone
from .models import RechargeCode, DCPackOrder
from accounts.services import DCService


MANUAL_PAYMENT_METHODS = ['orange_money', 'wave', 'bank_transfer', 'cash']
PACK_CREDIT_TRANSACTION_TYPES = ['purchase', 'manual_payment']


class DCPackOrderService:
    """Service centralisé pour finaliser une commande de pack DC."""

    @staticmethod
    def has_dc_credit(order):
        """Vérifie si les DC ont déjà été crédités pour cette commande."""
        from accounts.models import DCTransaction

        return DCTransaction.objects.filter(
            user=order.user,
            related_content_type='dc_pack_order',
            related_content_id=order.id,
            transaction_type__in=PACK_CREDIT_TRANSACTION_TYPES,
            amount__gt=0,
        ).exists()

    @staticmethod
    def get_orders_missing_credit():
        """Commandes complétées sans transaction DC associée."""
        from accounts.models import DCTransaction

        credited_order_ids = DCTransaction.objects.filter(
            related_content_type='dc_pack_order',
            transaction_type__in=PACK_CREDIT_TRANSACTION_TYPES,
            amount__gt=0,
            related_content_id__isnull=False,
        ).values_list('related_content_id', flat=True)

        return DCPackOrder.objects.filter(
            status='completed',
        ).exclude(
            id__in=credited_order_ids,
        ).select_related('user', 'pack')

    @staticmethod
    def _transaction_type_for_order(order):
        if order.payment_method in MANUAL_PAYMENT_METHODS:
            return 'manual_payment'
        return 'purchase'

    @staticmethod
    @transaction.atomic
    def complete_order(order, transaction_type, description, admin_notes=''):
        """
        Marque une commande comme complétée et crédite les DC.
        Idempotent : ne crédite pas deux fois la même commande.
        """
        order = DCPackOrder.objects.select_for_update().get(pk=order.pk)

        if order.status == 'completed' and DCPackOrderService.has_dc_credit(order):
            return True, "Commande déjà complétée et créditée."

        if not order.user:
            return False, "Utilisateur introuvable dans la commande."
        if not order.dc_amount or order.dc_amount <= 0:
            return False, f"Montant DC invalide: {order.dc_amount}"

        if DCPackOrderService.has_dc_credit(order):
            if order.status != 'completed':
                order.status = 'completed'
                order.completed_at = order.completed_at or timezone.now()
                if admin_notes:
                    order.admin_notes = admin_notes
                order.save()
            return True, "Les DC ont déjà été crédités pour cette commande."

        balance_before = order.user.dc_balance

        DCService.add_dc(
            user=order.user,
            amount=order.dc_amount,
            transaction_type=transaction_type,
            description=description,
            content_type='dc_pack_order',
            content_id=order.id,
        )

        order.user.refresh_from_db()
        balance_after = order.user.dc_balance

        order.status = 'completed'
        order.completed_at = order.completed_at or timezone.now()
        if admin_notes:
            order.admin_notes = admin_notes
        order.save()

        return True, (
            f"{order.dc_amount} DC crédités à {order.user.email} "
            f"(solde: {balance_before} -> {balance_after})."
        )

    @staticmethod
    @transaction.atomic
    def recredit_missing_order(order, admin_notes=''):
        """
        Recrédite les DC pour une commande déjà marquée « Complétée »
        mais jamais créditée (bug historique admin).
        """
        order = DCPackOrder.objects.select_for_update().get(pk=order.pk)

        if order.status != 'completed':
            return False, "Seules les commandes « Complétées » peuvent être recréditées."

        if DCPackOrderService.has_dc_credit(order):
            return False, "Les DC ont déjà été crédités pour cette commande."

        if not order.user:
            return False, "Utilisateur introuvable dans la commande."
        if not order.dc_amount or order.dc_amount <= 0:
            return False, f"Montant DC invalide: {order.dc_amount}"

        transaction_type = DCPackOrderService._transaction_type_for_order(order)
        pack_name = order.pack.name if order.pack else "Pack DC"
        balance_before = order.user.dc_balance

        DCService.add_dc(
            user=order.user,
            amount=order.dc_amount,
            transaction_type=transaction_type,
            description=f'Recrédit commande #{order.id} — {pack_name}',
            content_type='dc_pack_order',
            content_id=order.id,
        )

        order.user.refresh_from_db()
        balance_after = order.user.dc_balance

        if admin_notes:
            note = f"[Recrédit] {admin_notes}"
            order.admin_notes = f"{order.admin_notes}\n{note}".strip() if order.admin_notes else note
            order.save(update_fields=['admin_notes'])

        return True, (
            f"Recrédit effectué : {order.dc_amount} DC ajoutés à {order.user.email} "
            f"(solde: {balance_before} -> {balance_after})."
        )


class RechargeCodeService:
    """Service pour gérer les codes de recharge DC."""

    @staticmethod
    def generate_code(length=12):
        """Génère un code de recharge aléatoire."""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    @transaction.atomic
    def create_recharge_code(dc_amount, created_by, expires_at=None, notes=''):
        """
        Crée un nouveau code de recharge.

        Args:
            dc_amount: Montant DC du code
            created_by: Utilisateur qui crée le code
            expires_at: Date d'expiration (optionnel)
            notes: Notes sur le code

        Returns:
            RechargeCode: Le code créé
        """
        while True:
            code = RechargeCodeService.generate_code()
            if not RechargeCode.objects.filter(code=code).exists():
                break

        return RechargeCode.objects.create(
            code=code,
            dc_amount=dc_amount,
            created_by=created_by,
            expires_at=expires_at,
            notes=notes
        )

    @staticmethod
    @transaction.atomic
    def use_recharge_code(user, code_str):
        """
        Utilise un code de recharge pour un utilisateur.

        Args:
            user: Utilisateur qui utilise le code
            code_str: Code de recharge à utiliser

        Returns:
            tuple: (success, message, transaction)
        """
        try:
            recharge_code = RechargeCode.objects.get(code=code_str)
        except RechargeCode.DoesNotExist:
            return False, "Code de recharge invalide.", None

        if not recharge_code.is_valid():
            if recharge_code.status == 'used':
                return False, "Ce code a déjà été utilisé.", None
            elif recharge_code.status == 'expired':
                return False, "Ce code a expiré.", None
            elif recharge_code.status == 'cancelled':
                return False, "Ce code a été annulé.", None
            else:
                return False, "Ce code n'est pas disponible.", None

        dc_transaction = DCService.add_dc(
            user=user,
            amount=recharge_code.dc_amount,
            transaction_type='recharge_code',
            description=f'Recharge code: {code_str}'
        )

        recharge_code.status = 'used'
        recharge_code.used_by = user
        recharge_code.used_at = timezone.now()
        recharge_code.save()

        return True, f"Recharge réussie ! Vous avez reçu {recharge_code.dc_amount} DC.", dc_transaction

    @staticmethod
    def get_user_recharge_codes(user):
        """Récupère les codes de recharge créés par un utilisateur."""
        return RechargeCode.objects.filter(created_by=user).order_by('-created_at')


class ManualPaymentService:
    """Service pour gérer les paiements manuels."""

    @staticmethod
    @transaction.atomic
    def create_manual_order(user, pack, payment_method, transaction_reference=''):
        """
        Crée une commande de paiement manuel.

        Args:
            user: Utilisateur qui effectue la commande
            pack: Pack DC à acheter
            payment_method: Méthode de paiement (orange_money, wave, etc.)
            transaction_reference: Référence de transaction (optionnel)

        Returns:
            DCPackOrder: La commande créée
        """
        return DCPackOrder.objects.create(
            user=user,
            pack=pack,
            dc_amount=pack.dc_amount,
            price_paid_cfa=pack.price_cfa if pack.price_cfa else pack.price_eur,
            payment_method=payment_method,
            transaction_reference=transaction_reference,
            status='pending'
        )

    @staticmethod
    @transaction.atomic
    def validate_manual_payment(order_id, admin_notes=''):
        """
        Valide un paiement manuel et crédite les DC à l'utilisateur.

        Args:
            order_id: ID de la commande à valider
            admin_notes: Notes de l'administrateur

        Returns:
            tuple: (success, message)
        """
        try:
            order = DCPackOrder.objects.get(id=order_id)
        except DCPackOrder.DoesNotExist:
            return False, "Commande introuvable."

        if order.status != 'pending':
            return False, f"La commande est déjà {order.get_status_display()}."

        if order.payment_method not in MANUAL_PAYMENT_METHODS:
            return False, "Cette commande ne peut pas être validée manuellement."

        pack_name = order.pack.name if order.pack else "Pack DC"
        return DCPackOrderService.complete_order(
            order=order,
            transaction_type='manual_payment',
            description=f'Achat pack DC: {pack_name}',
            admin_notes=admin_notes,
        )

    @staticmethod
    @transaction.atomic
    def reject_manual_payment(order_id, admin_notes=''):
        """
        Rejette un paiement manuel.

        Args:
            order_id: ID de la commande à rejeter
            admin_notes: Notes de l'administrateur

        Returns:
            tuple: (success, message)
        """
        try:
            order = DCPackOrder.objects.get(id=order_id)
        except DCPackOrder.DoesNotExist:
            return False, "Commande introuvable."

        if order.status != 'pending':
            return False, f"La commande est déjà {order.get_status_display()}."

        order.status = 'cancelled'
        order.admin_notes = admin_notes
        order.save()

        return True, "Paiement rejeté. La commande a été annulée."

    @staticmethod
    def get_pending_orders():
        """Récupère les commandes en attente de validation."""
        return DCPackOrder.objects.filter(
            status='pending',
            payment_method__in=MANUAL_PAYMENT_METHODS,
        ).order_by('-created_at')
