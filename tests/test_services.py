"""
Tests unitaires pour les services DECEL.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import DCTransaction
from accounts.services import DCService
from gamification.models import XPLog, Badge, UserBadge
from gamification.services import XPService
from skills.models import Subject, UserSkill
from skills.services import SkillService

User = get_user_model()


class DCServiceTest(TestCase):
    """Tests pour le service DC."""

    def setUp(self):
        """Configuration initiale des tests."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_add_dc(self):
        """Test l'ajout de DC à un utilisateur."""
        initial_balance = self.user.dc_balance
        DCService.add_dc(
            user=self.user,
            amount=100,
            transaction_type='admin_grant',
            description='Test grant'
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, initial_balance + 100)

    def test_deduct_dc(self):
        """Test la déduction de DC d'un utilisateur."""
        self.user.dc_balance = 100
        self.user.save()
        success, message, transaction = DCService.deduct_dc(
            user=self.user,
            amount=50,
            transaction_type='purchase',
            description='Test purchase'
        )
        self.assertTrue(success)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 50)

    def test_deduct_dc_insufficient_balance(self):
        """Test la déduction de DC avec solde insuffisant."""
        self.user.dc_balance = 10
        self.user.save()
        success, message, transaction = DCService.deduct_dc(
            user=self.user,
            amount=50,
            transaction_type='purchase',
            description='Test purchase'
        )
        self.assertFalse(success)
        self.assertIn('solde dc insuffisant', message.lower())


class XPServiceTest(TestCase):
    """Tests pour le service XP."""

    def setUp(self):
        """Configuration initiale des tests."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_award_xp(self):
        """Test l'attribution d'XP."""
        initial_xp = self.user.total_xp
        XPService.award_xp(
            user=self.user,
            amount=100,
            reason='Test XP',
            action_type='test'
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_xp, initial_xp + 100)

    def test_calculate_level(self):
        """Test le calcul du niveau."""
        self.user.total_xp = 0
        self.assertEqual(XPService.calculate_level(0), 1)
        self.assertEqual(XPService.calculate_level(100), 2)
        self.assertEqual(XPService.calculate_level(400), 3)


class SkillServiceTest(TestCase):
    """Tests pour le service Skills."""

    def setUp(self):
        """Configuration initiale des tests."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.subject = Subject.objects.create(
            name='Mathématiques',
            description='Test subject'
        )

    def test_get_or_create_user_skill(self):
        """Test la création ou récupération d'une compétence utilisateur."""
        skill = SkillService.get_or_create_user_skill(self.user, self.subject)
        self.assertEqual(skill.user, self.user)
        self.assertEqual(skill.subject, self.subject)
        self.assertEqual(skill.skill_percentage, 0)

    def test_update_skill_from_exam(self):
        """Test la mise à jour de compétence après un examen."""
        SkillService.update_skill_from_exam(
            user=self.user,
            subject=self.subject,
            score=75,
            passed=True
        )
        skill = UserSkill.objects.get(user=self.user, subject=self.subject)
        self.assertGreater(skill.skill_percentage, 0)
        self.assertEqual(skill.total_exams_taken, 1)

    def test_get_weak_subjects(self):
        """Test la récupération des matières faibles."""
        SkillService.update_skill_from_exam(
            user=self.user,
            subject=self.subject,
            score=30,
            passed=False
        )
        weak_subjects = SkillService.get_weak_subjects(self.user, threshold=50)
        self.assertEqual(weak_subjects.count(), 1)
        self.assertEqual(weak_subjects.first().subject, self.subject)
