"""
Tests des modèles — contraintes, propriétés et méthodes métier.
Couvre : User, Contributor (is_pro), DCPack (dc_per_euro), DCPackOrder.
"""
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from accounts.models import User, Contributor, DCTransaction
from payments.models import DCPack, DCPackOrder
from skills.models import Subject, UserSkill


def make_user(email='model@test.com', dc_balance=0):
    return User.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='testpass123',
        first_name='Model',
        last_name='Test',
        dc_balance=dc_balance,
    )


class UserModelTest(TestCase):

    def test_get_full_name(self):
        user = make_user()
        user.first_name = 'Jean'
        user.last_name = 'Dupont'
        self.assertEqual(user.get_full_name(), 'Jean Dupont')

    def test_str_returns_email(self):
        user = make_user(email='hello@example.com')
        self.assertEqual(str(user), 'hello@example.com')

    def test_is_contributor_false_by_default(self):
        user = make_user()
        self.assertFalse(user.is_contributor())

    def test_is_contributor_true_when_active(self):
        user = make_user()
        admin = make_user(email='admin@test.com')
        Contributor.objects.create(user=user, is_active=True, created_by=admin)
        self.assertTrue(user.is_contributor())

    def test_is_contributor_false_when_inactive(self):
        user = make_user()
        admin = make_user(email='admin2@test.com')
        Contributor.objects.create(user=user, is_active=False, created_by=admin)
        self.assertFalse(user.is_contributor())

    def test_streak_shield_active_until_default_null(self):
        user = make_user()
        self.assertIsNone(user.streak_shield_active_until)

    def test_dc_balance_default_zero(self):
        user = User.objects.create_user(
            username='newuser', email='new@test.com', password='pass',
            first_name='New', last_name='User',
        )
        self.assertEqual(user.dc_balance, 0)


class ContributorIsPropTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.admin = make_user(email='admin@test.com')

    def test_free_plan_is_not_pro(self):
        c = Contributor.objects.create(user=self.user, plan='free', created_by=self.admin)
        self.assertFalse(c.is_pro)

    def test_pro_plan_without_expiry_is_pro(self):
        c = Contributor.objects.create(
            user=self.user, plan='pro', plan_expires_at=None, created_by=self.admin
        )
        self.assertTrue(c.is_pro)

    def test_pro_plan_future_expiry_is_pro(self):
        future = timezone.now() + timedelta(days=30)
        c = Contributor.objects.create(
            user=self.user, plan='pro', plan_expires_at=future, created_by=self.admin
        )
        self.assertTrue(c.is_pro)

    def test_pro_plan_expired_is_not_pro(self):
        past = timezone.now() - timedelta(days=1)
        c = Contributor.objects.create(
            user=self.user, plan='pro', plan_expires_at=past, created_by=self.admin
        )
        self.assertFalse(c.is_pro)

    def test_academy_plan_is_pro(self):
        c = Contributor.objects.create(user=self.user, plan='academy', created_by=self.admin)
        self.assertTrue(c.is_pro)


class DCPackModelTest(TestCase):

    def test_dc_per_cfa_calculation(self):
        from decimal import Decimal
        pack = DCPack(name='Test', dc_amount=500, price_cfa=Decimal('8000'))
        self.assertEqual(pack.dc_per_cfa, 0.06)  # 500 / 8000

    def test_dc_per_cfa_zero_price(self):
        from decimal import Decimal
        pack = DCPack(name='Gratuit', dc_amount=100, price_cfa=Decimal('0'))
        self.assertEqual(pack.dc_per_cfa, 0)

    def test_str_representation(self):
        from decimal import Decimal
        pack = DCPack(name='Starter', dc_amount=100, price_cfa=Decimal('2000'))
        self.assertIn('Starter', str(pack))
        self.assertIn('100 DC', str(pack))

    def test_active_by_default(self):
        pack = DCPack.objects.create(name='Pack Test', dc_amount=200, price_cfa='5000')
        self.assertTrue(pack.is_active)

    def test_popular_false_by_default(self):
        pack = DCPack.objects.create(name='Pack Défaut', dc_amount=100, price_eur='2.00')
        self.assertFalse(pack.is_popular)


class DCPackOrderModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.pack = DCPack.objects.create(name='Pack Test', dc_amount=500, price_eur='8.00')

    def test_order_default_status_pending(self):
        order = DCPackOrder.objects.create(
            user=self.user,
            pack=self.pack,
            dc_amount=500,
            price_paid_eur='8.00',
            stripe_session_id='cs_test_123',
        )
        self.assertEqual(order.status, 'pending')

    def test_order_str(self):
        order = DCPackOrder(
            user=self.user, dc_amount=500, status='pending'
        )
        self.assertIn('500 DC', str(order))

    def test_stripe_session_id_unique(self):
        DCPackOrder.objects.create(
            user=self.user, pack=self.pack, dc_amount=500,
            price_paid_eur='8.00', stripe_session_id='cs_unique_abc',
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            DCPackOrder.objects.create(
                user=self.user, pack=self.pack, dc_amount=500,
                price_paid_eur='8.00', stripe_session_id='cs_unique_abc',
            )


class UserSkillModelTest(TestCase):

    def test_str_representation(self):
        user = make_user()
        subject = Subject.objects.create(name='Maths')
        skill = UserSkill(user=user, subject=subject, skill_percentage=72)
        self.assertIn('72%', str(skill))
        self.assertIn('Maths', str(skill))

    def test_unique_together_user_subject(self):
        from django.db import IntegrityError
        user = make_user()
        subject = Subject.objects.create(name='Physique Unique')
        UserSkill.objects.create(user=user, subject=subject, skill_percentage=50)
        with self.assertRaises(IntegrityError):
            UserSkill.objects.create(user=user, subject=subject, skill_percentage=60)
