from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Subject, UserSkill
from django.conf import settings


class SkillService:
    """
    Service for managing user skills with recency-weighted calculation.
    Recent performance has higher impact on skill level.
    """
    
    # Recency decay factor (older actions have less impact)
    RECENCY_DAYS = 30  # Consider actions from last 30 days as recent
    
    @staticmethod
    def get_or_create_user_skill(user, subject: Subject) -> UserSkill:
        """Get or create a UserSkill record for a user and subject."""
        skill, created = UserSkill.objects.get_or_create(
            user=user,
            subject=subject,
            defaults={'skill_percentage': 0}
        )
        return skill
    
    @staticmethod
    def calculate_recency_weight(action_date) -> float:
        """
        Calculate recency weight for an action.
        Recent actions (within RECENCY_DAYS) get higher weight.
        
        Args:
            action_date: DateTime of the action
        
        Returns:
            float: Weight between 0.0 and 1.0
        """
        days_ago = (timezone.now() - action_date).days
        
        if days_ago <= SkillService.RECENCY_DAYS:
            # Linear decay: 1.0 for today, decreasing to 0.5 at RECENCY_DAYS
            return 1.0 - (0.5 * (days_ago / SkillService.RECENCY_DAYS))
        else:
            # Older actions get minimal weight
            return 0.3
    
    @staticmethod
    @transaction.atomic
    def update_skill_from_exam(user, subject: Subject, score: int, passed: bool):
        """
        Update user skill after completing an exam.
        Uses recency-weighted calculation.
        
        Args:
            user: The user
            subject: The subject of the exam
            score: Exam score (0-100)
            passed: Whether the user passed the exam
        """
        skill = SkillService.get_or_create_user_skill(user, subject)
        
        # Get recency weight for this action
        recency_weight = 1.0  # Current action gets full weight
        
        # Calculate new skill using weighted average
        # Current skill has weight based on its recency
        current_skill_weight = SkillService.calculate_recency_weight(skill.last_activity)
        
        # New skill = (old_skill * old_weight + new_score * new_weight) / (old_weight + new_weight)
        total_weight = current_skill_weight + recency_weight
        new_skill = int((skill.skill_percentage * current_skill_weight + score * recency_weight) / total_weight)
        
        # Update skill record
        skill.skill_percentage = min(100, max(0, new_skill))
        skill.total_exams_taken += 1
        skill.last_activity = timezone.now()
        skill.save()
        
        return skill
    
    @staticmethod
    @transaction.atomic
    def update_skill_from_td(user, subject: Subject, score: int):
        """
        Update user skill after completing a TD (Travaux Dirigés).
        TD has medium impact on skill.
        
        Args:
            user: The user
            subject: The subject of the TD
            score: TD score (0-100)
        """
        skill = SkillService.get_or_create_user_skill(user, subject)
        
        # TD has lower impact than exams (0.7 weight)
        recency_weight = 0.7
        current_skill_weight = SkillService.calculate_recency_weight(skill.last_activity)
        
        total_weight = current_skill_weight + recency_weight
        new_skill = int((skill.skill_percentage * current_skill_weight + score * recency_weight) / total_weight)
        
        skill.skill_percentage = min(100, max(0, new_skill))
        skill.total_td_completed += 1
        skill.last_activity = timezone.now()
        skill.save()
        
        return skill
    
    @staticmethod
    @transaction.atomic
    def update_skill_from_course(user, subject: Subject):
        """
        Update user skill after reading a course.
        Course has low impact on skill (engagement metric).
        
        Args:
            user: The user
            subject: The subject of the course
        """
        skill = SkillService.get_or_create_user_skill(user, subject)
        
        # Course has minimal impact (0.3 weight) - mainly for engagement
        recency_weight = 0.3
        current_skill_weight = SkillService.calculate_recency_weight(skill.last_activity)
        
        total_weight = current_skill_weight + recency_weight
        # Course doesn't provide a score, so we slightly boost current skill
        new_skill = int((skill.skill_percentage * current_skill_weight + skill.skill_percentage * recency_weight) / total_weight)
        
        skill.skill_percentage = min(100, max(0, new_skill))
        skill.total_courses_read += 1
        skill.last_activity = timezone.now()
        skill.save()
        
        return skill
    
    @staticmethod
    def get_user_skills(user):
        """
        Get all skills for a user, ordered by skill percentage.
        Returns queryset with subject information.
        """
        return UserSkill.objects.filter(user=user).select_related('subject')
    
    @staticmethod
    def get_weak_subjects(user, threshold: int = 50):
        """
        Get subjects where user's skill is below threshold.
        Used for recommendation targeting.
        
        Args:
            user: The user
            threshold: Skill percentage threshold (default 50)
        
        Returns:
            QuerySet of UserSkill below threshold
        """
        return UserSkill.objects.filter(
            user=user,
            skill_percentage__lt=threshold
        ).select_related('subject')
    
    @staticmethod
    def get_strong_subjects(user, threshold: int = 70):
        """
        Get subjects where user's skill is above threshold.
        Used for advancement recommendations.
        
        Args:
            user: The user
            threshold: Skill percentage threshold (default 70)
        
        Returns:
            QuerySet of UserSkill above threshold
        """
        return UserSkill.objects.filter(
            user=user,
            skill_percentage__gte=threshold
        ).select_related('subject')
