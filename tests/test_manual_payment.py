"""Tests pour la validation des paiements manuels de packs DC."""
from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.models import DCTransaction
from payments.models import DCPack, DCPackOrder
from payments.services import ManualPaymentService, DCPackOrderService

User = get_user_model()


def make_user(email='buyer@test.com', dc_balance=0):
    return User.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='testpass123',
        first_name='Test',
        last_name='Buyer',
        dc_balance=dc_balance,
    )


class ManualPaymentValidationTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.pack = DCPack.objects.create(
            name='Pack Starter',
            dc_amount=200,
            price_cfa=5000,
        )

    def test_validate_manual_payment_credits_user(self):
        order = DCPackOrder.objects.create(
            user=self.user,
            pack=self.pack,
            dc_amount=self.pack.dc_amount,
            price_paid_cfa=5000,
            payment_method='orange_money',
            status='pending',
        )

        success, message = ManualPaymentService.validate_manual_payment(order.id)

        self.assertTrue(success)
        self.user.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 200)
        self.assertEqual(order.status, 'completed')
        self.assertIsNotNone(order.completed_at)
        self.assertTrue(
            DCTransaction.objects.filter(
                user=self.user,
                transaction_type='manual_payment',
                amount=200,
            ).exists()
        )

    def test_validate_manual_payment_is_idempotent(self):
        order = DCPackOrder.objects.create(
            user=self.user,
            pack=self.pack,
            dc_amount=self.pack.dc_amount,
            price_paid_cfa=5000,
            payment_method='wave',
            status='pending',
        )

        ManualPaymentService.validate_manual_payment(order.id)
        success, message = ManualPaymentService.validate_manual_payment(order.id)

        self.assertFalse(success)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 200)
        self.assertEqual(DCTransaction.objects.filter(user=self.user).count(), 1)

    def test_recredit_missing_order_for_completed_without_transaction(self):
        order = DCPackOrder.objects.create(
            user=self.user,
            pack=self.pack,
            dc_amount=self.pack.dc_amount,
            price_paid_cfa=5000,
            payment_method='orange_money',
            status='completed',
        )

        self.assertFalse(DCPackOrderService.has_dc_credit(order))

        success, message = DCPackOrderService.recredit_missing_order(order)

        self.assertTrue(success)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 200)
        self.assertTrue(DCPackOrderService.has_dc_credit(order))

    def test_recredit_missing_order_is_idempotent(self):
        order = DCPackOrder.objects.create(
            user=self.user,
            pack=self.pack,
            dc_amount=self.pack.dc_amount,
            price_paid_cfa=5000,
            payment_method='bank_transfer',
            status='completed',
        )

        DCPackOrderService.recredit_missing_order(order)
        success, message = DCPackOrderService.recredit_missing_order(order)

        self.assertFalse(success)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 200)
        self.assertEqual(DCTransaction.objects.filter(user=self.user).count(), 1)

    def test_get_orders_missing_credit(self):
        missing = DCPackOrder.objects.create(
            user=self.user,
            pack=self.pack,
            dc_amount=self.pack.dc_amount,
            price_paid_cfa=5000,
            payment_method='cash',
            status='completed',
        )
        credited = DCPackOrder.objects.create(
            user=self.user,
            pack=self.pack,
            dc_amount=self.pack.dc_amount,
            price_paid_cfa=5000,
            payment_method='wave',
            status='pending',
        )
        ManualPaymentService.validate_manual_payment(credited.id)

        missing_ids = list(DCPackOrderService.get_orders_missing_credit().values_list('id', flat=True))

        self.assertIn(missing.id, missing_ids)
        self.assertNotIn(credited.id, missing_ids)

    def test_complete_order_service_credits_stripe_order(self):
        order = DCPackOrder.objects.create(
            user=self.user,
            pack=self.pack,
            dc_amount=self.pack.dc_amount,
            price_paid_cfa=5000,
            payment_method='stripe',
            status='pending',
        )

        success, message = DCPackOrderService.complete_order(
            order=order,
            transaction_type='purchase',
            description='Achat pack DC via Stripe',
        )

        self.assertTrue(success)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 200)
