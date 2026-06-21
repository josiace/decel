"""
Tests pour XPService — calcul de niveaux et attribution d'XP.
Couvre : award_xp, calculate_level, get_level_progress, check_and_award_badges.
"""
from django.test import TestCase
from accounts.models import User
from gamification.models import XPLog, Badge, UserBadge
from gamification.services import XPService


def make_user(email='xpuser@test.com', total_xp=0):
    user = User.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='testpass123',
        first_name='XP',
        last_name='User',
        total_xp=total_xp,
    )
    user.level = XPService.calculate_level(total_xp)
    user.save()
    return user


class CalculateLevelTest(TestCase):

    def test_level_1_at_zero_xp(self):
        self.assertEqual(XPService.calculate_level(0), 1)

    def test_level_1_below_100_xp(self):
        self.assertEqual(XPService.calculate_level(99), 1)

    def test_level_2_at_100_xp(self):
        self.assertEqual(XPService.calculate_level(100), 2)

    def test_level_2_at_399_xp(self):
        self.assertEqual(XPService.calculate_level(399), 2)

    def test_level_3_at_400_xp(self):
        self.assertEqual(XPService.calculate_level(400), 3)

    def test_level_increases_with_xp(self):
        prev = 1
        for xp in [100, 400, 900, 1600, 2500]:
            level = XPService.calculate_level(xp)
            self.assertGreaterEqual(level, prev)
            prev = level

    def test_formula_consistency(self):
        """floor(sqrt(xp / 100)) + 1 = expected level."""
        import math
        for xp in [0, 50, 100, 200, 400, 900, 1600]:
            expected = int(math.sqrt(xp / 100)) + 1 if xp >= 100 else 1
            self.assertEqual(XPService.calculate_level(xp), expected)


class AwardXPTest(TestCase):

    def setUp(self):
        self.user = make_user(total_xp=0)

    def test_award_xp_increases_total(self):
        XPService.award_xp(self.user, 100, 'Examen réussi', 'exam')
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_xp, 100)

    def test_award_xp_creates_log(self):
        XPService.award_xp(self.user, 50, 'TD complété', 'td')
        log = XPLog.objects.get(user=self.user)
        self.assertEqual(log.amount, 50)
        self.assertEqual(log.action_type, 'td')

    def test_award_xp_updates_level(self):
        self.assertEqual(self.user.level, 1)
        XPService.award_xp(self.user, 100, 'Examen', 'exam')
        self.user.refresh_from_db()
        self.assertEqual(self.user.level, 2)

    def test_award_xp_returns_log_instance(self):
        log = XPService.award_xp(self.user, 20, 'Cours lu', 'course')
        self.assertIsInstance(log, XPLog)


class LevelProgressTest(TestCase):

    def test_progress_at_level_1_no_xp(self):
        user = make_user(total_xp=0)
        progress = XPService.get_level_progress(user)
        self.assertEqual(progress['current_level'], 1)
        self.assertGreaterEqual(progress['progress_percentage'], 0)
        self.assertLessEqual(progress['progress_percentage'], 100)

    def test_progress_percentage_increases(self):
        user = make_user(total_xp=50)
        p1 = XPService.get_level_progress(user)
        user.total_xp = 90
        user.save()
        p2 = XPService.get_level_progress(user)
        self.assertGreater(p2['progress_percentage'], p1['progress_percentage'])

    def test_xp_for_next_level_always_greater_than_current(self):
        user = make_user(total_xp=100)
        progress = XPService.get_level_progress(user)
        self.assertGreater(progress['xp_for_next_level'], progress['current_xp'])


class BadgeAwardTest(TestCase):

    def setUp(self):
        self.user = make_user(total_xp=0)

    def test_badge_awarded_when_xp_threshold_met(self):
        Badge.objects.create(
            name='Débutant',
            description='100 XP atteints',
            xp_threshold=100,
            is_active=True,
        )
        XPService.award_xp(self.user, 100, 'Examen', 'exam')
        self.assertTrue(UserBadge.objects.filter(user=self.user).exists())

    def test_badge_not_awarded_twice(self):
        Badge.objects.create(
            name='Badge Unique',
            description='Test',
            xp_threshold=50,
            is_active=True,
        )
        XPService.award_xp(self.user, 50, 'First', 'exam')
        XPService.award_xp(self.user, 50, 'Second', 'exam')
        count = UserBadge.objects.filter(user=self.user).count()
        self.assertEqual(count, 1)

    def test_inactive_badge_not_awarded(self):
        Badge.objects.create(
            name='Badge Inactif',
            description='Test',
            xp_threshold=10,
            is_active=False,
        )
        XPService.award_xp(self.user, 100, 'Examen', 'exam')
        self.assertFalse(UserBadge.objects.filter(user=self.user).exists())
