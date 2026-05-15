from django.db import transaction
from django.utils import timezone
from .models import XPLog, Badge, UserBadge
from django.conf import settings


class XPService:
    """
    Service for managing XP (Experience Points) progression.
    XP is used for progression tracking and level calculation.
    XP is NOT a currency - it cannot be spent.
    """
    
    # XP amounts for different actions
    XP_EXAM_PASSED = 100
    XP_EXAM_FAILED = 50
    XP_TD_COMPLETED = 40
    XP_COURSE_READ = 20
    
    # Level calculation: level = sqrt(total_xp / 100)
    # Level 1: 0-99 XP
    # Level 2: 100-399 XP
    # Level 3: 400-899 XP
    # Level 4: 900-1599 XP
    # Level 5: 1600-2499 XP
    # etc.
    
    @staticmethod
    @transaction.atomic
    def award_xp(user, amount: int, reason: str, action_type: str, **kwargs) -> XPLog:
        """
        Award XP to a user and update their level.
        
        Args:
            user: The user to award XP to
            amount: Amount of XP to award
            reason: Description of why XP was awarded
            action_type: Type of action (exam, td, course, etc.)
            **kwargs: Optional related object IDs
        
        Returns:
            XPLog: The created XP log entry
        """
        # Create XP log
        xp_log = XPLog.objects.create(
            user=user,
            amount=amount,
            reason=reason,
            action_type=action_type,
            related_exam_id=kwargs.get('exam_id'),
            related_td_id=kwargs.get('td_id'),
            related_course_id=kwargs.get('course_id'),
        )
        
        # Update user's total XP
        user.total_xp += amount
        
        # Recalculate level
        user.level = XPService.calculate_level(user.total_xp)
        
        user.save()
        
        # Check for badge eligibility
        XPService.check_and_award_badges(user)
        
        return xp_log
    
    @staticmethod
    def calculate_level(total_xp: int) -> int:
        """
        Calculate level based on total XP.
        Formula: level = floor(sqrt(total_xp / 100)) + 1
        
        Args:
            total_xp: Total XP accumulated
        
        Returns:
            int: Current level
        """
        if total_xp < 100:
            return 1
        return int((total_xp / 100) ** 0.5) + 1
    
    @staticmethod
    def get_xp_for_next_level(current_level: int) -> int:
        """
        Calculate XP required to reach the next level.
        Formula: xp_needed = (level^2) * 100
        
        Args:
            current_level: Current user level
        
        Returns:
            int: XP needed for next level
        """
        next_level = current_level + 1
        return (next_level ** 2) * 100
    
    @staticmethod
    def get_level_progress(user) -> dict:
        """
        Get user's progress towards the next level.
        
        Args:
            user: The user
        
        Returns:
            dict: Progress information including current XP, next level XP, and percentage
        """
        current_level = user.level
        current_xp = user.total_xp
        
        # XP needed for current level
        xp_for_current_level = ((current_level - 1) ** 2) * 100 if current_level > 1 else 0
        
        # XP needed for next level
        xp_for_next_level = XPService.get_xp_for_next_level(current_level)
        
        # XP earned in current level
        xp_in_current_level = current_xp - xp_for_current_level
        
        # XP needed to complete current level
        xp_needed_for_level = xp_for_next_level - xp_for_current_level
        
        # Percentage progress
        progress_percentage = int((xp_in_current_level / xp_needed_for_level) * 100) if xp_needed_for_level > 0 else 100
        
        return {
            'current_level': current_level,
            'current_xp': current_xp,
            'xp_for_next_level': xp_for_next_level,
            'xp_in_current_level': xp_in_current_level,
            'xp_needed_for_level': xp_needed_for_level,
            'progress_percentage': progress_percentage,
        }
    
    @staticmethod
    @transaction.atomic
    def check_and_award_badges(user):
        """
        Check if user is eligible for any badges and award them.
        """
        # Get all active badges
        badges = Badge.objects.filter(is_active=True)
        
        for badge in badges:
            # Skip if user already has this badge
            if UserBadge.objects.filter(user=user, badge=badge).exists():
                continue
            
            # Check XP threshold
            if badge.xp_threshold and user.total_xp < badge.xp_threshold:
                continue
            
            # Check exam count threshold
            if badge.exam_count_threshold:
                from exams.models import ExamSession
                exam_count = ExamSession.objects.filter(
                    user=user,
                    is_completed=True
                ).count()
                if exam_count < badge.exam_count_threshold:
                    continue
            
            # Check skill threshold
            if badge.skill_threshold:
                from skills.models import UserSkill
                has_required_skill = UserSkill.objects.filter(
                    user=user,
                    skill_percentage__gte=badge.skill_threshold
                ).exists()
                if not has_required_skill:
                    continue
            
            # Award badge
            UserBadge.objects.create(user=user, badge=badge)
