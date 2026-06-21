"""
Tests pour SkillService — suivi de compétences avec pondération temporelle.
Couvre : update_skill_from_exam, update_skill_from_td, update_skill_from_course,
         get_weak_subjects, get_strong_subjects, calculate_recency_weight.
"""
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from skills.models import Subject, UserSkill
from skills.services import SkillService


def make_user(email='skilluser@test.com'):
    return User.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='testpass123',
        first_name='Skill',
        last_name='User',
    )


class SkillServiceExamTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.subject = Subject.objects.create(name='Physique Test')

    def test_exam_creates_skill_if_not_exists(self):
        self.assertFalse(UserSkill.objects.filter(user=self.user, subject=self.subject).exists())
        SkillService.update_skill_from_exam(self.user, self.subject, score=80, passed=True)
        self.assertTrue(UserSkill.objects.filter(user=self.user, subject=self.subject).exists())

    def test_exam_increments_exam_count(self):
        SkillService.update_skill_from_exam(self.user, self.subject, score=70, passed=True)
        skill = UserSkill.objects.get(user=self.user, subject=self.subject)
        self.assertEqual(skill.total_exams_taken, 1)
        SkillService.update_skill_from_exam(self.user, self.subject, score=80, passed=True)
        skill.refresh_from_db()
        self.assertEqual(skill.total_exams_taken, 2)

    def test_exam_skill_stays_in_0_100(self):
        SkillService.update_skill_from_exam(self.user, self.subject, score=0, passed=False)
        skill = UserSkill.objects.get(user=self.user, subject=self.subject)
        self.assertGreaterEqual(skill.skill_percentage, 0)

        SkillService.update_skill_from_exam(self.user, self.subject, score=100, passed=True)
        skill.refresh_from_db()
        self.assertLessEqual(skill.skill_percentage, 100)

    def test_high_score_increases_skill(self):
        skill = UserSkill.objects.create(user=self.user, subject=self.subject, skill_percentage=40)
        SkillService.update_skill_from_exam(self.user, self.subject, score=100, passed=True)
        skill.refresh_from_db()
        self.assertGreater(skill.skill_percentage, 40)

    def test_low_score_decreases_skill(self):
        skill = UserSkill.objects.create(user=self.user, subject=self.subject, skill_percentage=80)
        SkillService.update_skill_from_exam(self.user, self.subject, score=10, passed=False)
        skill.refresh_from_db()
        self.assertLess(skill.skill_percentage, 80)


class SkillServiceTDTest(TestCase):

    def setUp(self):
        self.user = make_user(email='tdskill@test.com')
        self.subject = Subject.objects.create(name='Chimie Test')

    def test_td_increments_td_count(self):
        SkillService.update_skill_from_td(self.user, self.subject, score=75)
        skill = UserSkill.objects.get(user=self.user, subject=self.subject)
        self.assertEqual(skill.total_td_completed, 1)

    def test_td_has_lower_impact_than_exam(self):
        """
        TD a un poids de 0.7 vs 1.0 pour les examens.
        À partir du même niveau de base, un score identique via TD
        doit modifier le skill moins qu'un examen.
        """
        subject2 = Subject.objects.create(name='Chimie Test 2')
        base = 40

        # Exam
        UserSkill.objects.create(user=self.user, subject=self.subject, skill_percentage=base)
        SkillService.update_skill_from_exam(self.user, self.subject, score=100, passed=True)
        skill_exam = UserSkill.objects.get(user=self.user, subject=self.subject)

        # TD
        UserSkill.objects.create(user=self.user, subject=subject2, skill_percentage=base)
        SkillService.update_skill_from_td(self.user, subject2, score=100)
        skill_td = UserSkill.objects.get(user=self.user, subject=subject2)

        self.assertGreater(skill_exam.skill_percentage, skill_td.skill_percentage)


class SkillServiceCourseTest(TestCase):

    def setUp(self):
        self.user = make_user(email='courseskill@test.com')
        self.subject = Subject.objects.create(name='Bio Test')

    def test_course_increments_course_count(self):
        SkillService.update_skill_from_course(self.user, self.subject)
        skill = UserSkill.objects.get(user=self.user, subject=self.subject)
        self.assertEqual(skill.total_courses_read, 1)

    def test_course_skill_stays_stable(self):
        """Un cours ne doit pas réduire la compétence existante."""
        UserSkill.objects.create(user=self.user, subject=self.subject, skill_percentage=60)
        SkillService.update_skill_from_course(self.user, self.subject)
        skill = UserSkill.objects.get(user=self.user, subject=self.subject)
        self.assertGreaterEqual(skill.skill_percentage, 60)


class SkillServiceQueryTest(TestCase):

    def setUp(self):
        self.user = make_user(email='queryskill@test.com')
        s1 = Subject.objects.create(name='Matière Faible')
        s2 = Subject.objects.create(name='Matière Forte')
        UserSkill.objects.create(user=self.user, subject=s1, skill_percentage=30)
        UserSkill.objects.create(user=self.user, subject=s2, skill_percentage=80)

    def test_get_weak_subjects_below_threshold(self):
        weak = SkillService.get_weak_subjects(self.user, threshold=50)
        self.assertEqual(weak.count(), 1)
        self.assertEqual(weak.first().skill_percentage, 30)

    def test_get_strong_subjects_above_threshold(self):
        strong = SkillService.get_strong_subjects(self.user, threshold=70)
        self.assertEqual(strong.count(), 1)
        self.assertEqual(strong.first().skill_percentage, 80)

    def test_no_weak_subjects_when_all_strong(self):
        weak = SkillService.get_weak_subjects(self.user, threshold=20)
        self.assertEqual(weak.count(), 0)


class RecencyWeightTest(TestCase):

    def test_today_weight_is_1(self):
        weight = SkillService.calculate_recency_weight(timezone.now())
        self.assertEqual(weight, 1.0)

    def test_old_action_has_low_weight(self):
        old_date = timezone.now() - timedelta(days=60)
        weight = SkillService.calculate_recency_weight(old_date)
        self.assertEqual(weight, 0.3)

    def test_recent_action_weight_between_05_and_1(self):
        date_15_days_ago = timezone.now() - timedelta(days=15)
        weight = SkillService.calculate_recency_weight(date_15_days_ago)
        self.assertGreater(weight, 0.5)
        self.assertLessEqual(weight, 1.0)
