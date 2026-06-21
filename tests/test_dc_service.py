"""
Tests pour DCService — gestion de la monnaie DC.
Couvre : add_dc, deduct_dc, daily_bonus, exam_reward, content_purchase, streak_shield.
"""
from datetime import date
from django.test import TestCase, override_settings
from accounts.models import User, DCTransaction
from accounts.services import DCService


def make_user(email='user@test.com', dc_balance=100, **kwargs):
    """Helper pour créer un utilisateur de test."""
    return User.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='testpass123',
        first_name='Test',
        last_name='User',
        dc_balance=dc_balance,
        **kwargs,
    )


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class DCServiceAddTest(TestCase):

    def setUp(self):
        self.user = make_user(dc_balance=100)

    def test_add_dc_increases_balance(self):
        DCService.add_dc(self.user, 50, 'exam_reward', 'Récompense test')
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 150)

    def test_add_dc_creates_transaction(self):
        DCService.add_dc(self.user, 50, 'exam_reward', 'Récompense test')
        tx = DCTransaction.objects.get(user=self.user, transaction_type='exam_reward')
        self.assertEqual(tx.amount, 50)
        self.assertEqual(tx.balance_after, 150)
        self.assertEqual(tx.description, 'Récompense test')

    def test_add_dc_zero_amount(self):
        DCService.add_dc(self.user, 0, 'admin_grant', 'Test zéro')
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 100)

    def test_add_dc_returns_transaction(self):
        tx = DCService.add_dc(self.user, 20, 'daily_bonus', 'Bonus')
        self.assertIsInstance(tx, DCTransaction)
        self.assertEqual(tx.amount, 20)


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class DCServiceDeductTest(TestCase):

    def setUp(self):
        self.user = make_user(dc_balance=100)

    def test_deduct_dc_success(self):
        success, msg, tx = DCService.deduct_dc(self.user, 30, 'purchase', 'Achat test')
        self.assertTrue(success)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 70)

    def test_deduct_dc_creates_negative_transaction(self):
        DCService.deduct_dc(self.user, 30, 'purchase', 'Achat test')
        tx = DCTransaction.objects.get(user=self.user)
        self.assertEqual(tx.amount, -30)
        self.assertEqual(tx.balance_after, 70)

    def test_deduct_dc_insufficient_balance(self):
        success, msg, tx = DCService.deduct_dc(self.user, 200, 'purchase', 'Trop cher')
        self.assertFalse(success)
        self.assertIsNone(tx)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 100)  # inchangé

    def test_deduct_dc_exact_balance(self):
        success, msg, tx = DCService.deduct_dc(self.user, 100, 'purchase', 'Tout dépenser')
        self.assertTrue(success)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 0)

    def test_deduct_dc_message_on_failure(self):
        success, msg, tx = DCService.deduct_dc(self.user, 9999, 'purchase', 'Impossible')
        self.assertIn('insuffisant', msg.lower())


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class DCServiceDailyBonusTest(TestCase):

    def setUp(self):
        self.user = make_user(dc_balance=0, current_streak=0)

    def test_daily_bonus_first_time(self):
        success, msg, tx = DCService.award_daily_bonus(self.user)
        self.assertTrue(success)
        self.assertIsNotNone(tx)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, DCService.DAILY_LOGIN_BONUS)

    def test_daily_bonus_only_once_per_day(self):
        DCService.award_daily_bonus(self.user)
        success2, msg2, tx2 = DCService.award_daily_bonus(self.user)
        self.assertFalse(success2)
        self.assertIsNone(tx2)

    def test_daily_bonus_streak_adds_extra(self):
        self.user.current_streak = 5
        self.user.save()
        success, msg, tx = DCService.award_daily_bonus(self.user)
        self.assertTrue(success)
        self.user.refresh_from_db()
        # Base 5 + streak bonus 5 = 10
        self.assertEqual(self.user.dc_balance, DCService.DAILY_LOGIN_BONUS + 5)

    def test_daily_bonus_streak_capped_at_10(self):
        self.user.current_streak = 50  # au-delà du cap
        self.user.save()
        DCService.award_daily_bonus(self.user)
        self.user.refresh_from_db()
        # Cap à 10 → total max = 5 + 10 = 15
        self.assertEqual(self.user.dc_balance, DCService.DAILY_LOGIN_BONUS + 10)


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class DCServiceExamRewardTest(TestCase):

    def setUp(self):
        self.user = make_user(dc_balance=0)

    def test_exam_reward_when_score_ge_50(self):
        tx = DCService.award_exam_reward(self.user, exam_id=1, score=60)
        self.assertIsNotNone(tx)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, DCService.EXAM_REWARD)

    def test_exam_reward_exactly_50(self):
        tx = DCService.award_exam_reward(self.user, exam_id=1, score=50)
        self.assertIsNotNone(tx)

    def test_no_reward_when_score_lt_50(self):
        tx = DCService.award_exam_reward(self.user, exam_id=1, score=49)
        self.assertIsNone(tx)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 0)

    def test_no_reward_score_zero(self):
        tx = DCService.award_exam_reward(self.user, exam_id=1, score=0)
        self.assertIsNone(tx)


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class DCServiceContentPurchaseTest(TestCase):

    def setUp(self):
        self.buyer = make_user(email='buyer@test.com', dc_balance=100)
        self.author = make_user(email='author@test.com', dc_balance=0)

    def test_purchase_deducts_from_buyer(self):
        DCService.process_content_purchase(self.buyer, 'course', 1, 20, self.author)
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.dc_balance, 80)

    def test_purchase_credits_author_75_percent(self):
        DCService.process_content_purchase(self.buyer, 'course', 1, 20, self.author)
        self.author.refresh_from_db()
        self.assertEqual(self.author.dc_balance, 15)  # 75% de 20

    def test_free_content_no_deduction(self):
        success, msg = DCService.process_content_purchase(self.buyer, 'course', 1, 0, self.author)
        self.assertTrue(success)
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.dc_balance, 100)  # inchangé

    def test_insufficient_balance_fails(self):
        success, msg = DCService.process_content_purchase(self.buyer, 'course', 1, 500, self.author)
        self.assertFalse(success)
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.dc_balance, 100)  # inchangé

    def test_author_does_not_get_commission_from_own_purchase(self):
        """Un créateur ne peut pas acheter son propre contenu et s'auto-créditer."""
        success, msg = DCService.process_content_purchase(self.author, 'course', 1, 20, self.author)
        # L'achat peut réussir techniquement, mais sans auto-commission
        # (DCService vérifie author != purchaser)
        if success:
            self.author.refresh_from_db()
            # Pas de commission auto versée
            commission = DCTransaction.objects.filter(
                user=self.author, transaction_type='sale'
            ).count()
            self.assertEqual(commission, 0)


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class DCServiceStreakShieldTest(TestCase):

    def setUp(self):
        self.user = make_user(dc_balance=50, current_streak=7)

    def test_streak_shield_costs_10_dc(self):
        DCService.activate_streak_shield(self.user)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 40)

    def test_streak_shield_sets_date(self):
        DCService.activate_streak_shield(self.user)
        self.user.refresh_from_db()
        self.assertEqual(self.user.streak_shield_active_until, date.today())

    def test_streak_shield_cannot_activate_twice(self):
        DCService.activate_streak_shield(self.user)
        success, msg = DCService.activate_streak_shield(self.user)
        self.assertFalse(success)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 40)  # un seul débit

    def test_streak_shield_fails_insufficient_balance(self):
        self.user.dc_balance = 5
        self.user.save()
        success, msg = DCService.activate_streak_shield(self.user)
        self.assertFalse(success)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 5)  # inchangé
