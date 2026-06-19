from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Avg, Q, F
from .models import Recommendation
from skills.services import SkillService
from skills.models import UserSkill, Subject
from accounts.models import User
from exams.models import ExamSession
from learning.models import Course, TD, CourseProgress, TDProgress
from datetime import timedelta
import math


class RecommendationService:
    """
    Service for generating adaptive learning recommendations.
    Analyzes user performance and suggests next learning actions.
    """
    
    @staticmethod
    @transaction.atomic
    def generate_recommendation(user, recommendation_type: str, context: dict = None) -> Recommendation:
        """
        Generate a recommendation based on user performance.
        
        Args:
            user: The user
            recommendation_type: Type of recommendation (review, advance, practice, learn)
            context: Additional context data (subject, score, etc.)
        
        Returns:
            Recommendation: The created recommendation
        """
        if context is None:
            context = {}
        
        # Generate title and description based on type
        title, description = RecommendationService._generate_recommendation_text(
            recommendation_type, context
        )
        
        # Set priority based on type
        priority = RecommendationService._get_priority_for_type(recommendation_type)
        
        # Create recommendation
        recommendation = Recommendation.objects.create(
            user=user,
            recommendation_type=recommendation_type,
            title=title,
            description=description,
            context=context,
            priority=priority,
        )
        
        return recommendation
    
    @staticmethod
    def _generate_recommendation_text(rec_type: str, context: dict) -> tuple:
        """Generate title and description for a recommendation type."""
        subject = context.get('subject', 'cette matière')
        score = context.get('exam_score', 0)
        
        if rec_type == 'review':
            title = f"Réviser {subject}"
            description = (
                f"Votre performance récente en {subject} ({score}%) indique une marge d'amélioration. "
                f"Nous recommandons de réviser le matériel du cours et de pratiquer avec des TD avant de tenter un autre examen."
            )
        elif rec_type == 'advance':
            title = f"Avancer en {subject}"
            description = (
                f"Excellent travail en {subject} ({score}%) ! Vous avez démontré une solide compréhension. "
                f"Envisagez de passer des examens plus difficiles ou d'explorer des sujets avancés."
            )
        elif rec_type == 'practice':
            title = f"Pratiquer {subject}"
            description = (
                f"Pour renforcer vos compétences en {subject}, complétez quelques TD (Travaux Dirigés). "
                f"Les exercices de pratique aideront à consolider votre compréhension."
            )
        elif rec_type == 'learn':
            title = f"Apprendre {subject}"
            description = (
                f"Commencez à apprendre {subject} en lisant le matériel du cours. "
                f"Construire une base solide est la clé du succès."
            )
        else:
            title = "Continuer l'Apprentissage"
            description = "Continuez votre excellent travail ! Poursuivez votre parcours d'apprentissage."
        
        return title, description
    
    @staticmethod
    def _get_priority_for_type(rec_type: str) -> int:
        """Get priority level for a recommendation type."""
        priorities = {
            'review': 9,      # High priority - fix weak areas
            'practice': 7,    # Medium-high - improve skills
            'learn': 5,       # Medium - new content
            'advance': 6,     # Medium - challenge strong areas
        }
        return priorities.get(rec_type, 5)
    
    @staticmethod
    def get_active_recommendations(user, limit: int = 5):
        """
        Get active (non-dismissed) recommendations for a user.
        
        Args:
            user: The user
            limit: Maximum number of recommendations to return
        
        Returns:
            QuerySet of active recommendations
        """
        return Recommendation.objects.filter(
            user=user,
            is_active=True,
            is_dismissed=False
        ).order_by('-priority', '-created_at')[:limit]
    
    @staticmethod
    @transaction.atomic
    def dismiss_recommendation(user, recommendation_id: int):
        """
        Mark a recommendation as dismissed by the user.
        
        Args:
            user: The user
            recommendation_id: ID of the recommendation to dismiss
        """
        try:
            recommendation = Recommendation.objects.get(
                id=recommendation_id,
                user=user
            )
            recommendation.is_dismissed = True
            recommendation.save()
        except Recommendation.DoesNotExist:
            pass
    
    @staticmethod
    @transaction.atomic
    def generate_recommendations_for_user(user):
        """
        Analyze user's skills and generate appropriate recommendations.
        Called periodically or after significant actions.
        
        Args:
            user: The user to analyze
        """
        skill_service = SkillService()
        
        # Get weak subjects (below 50%)
        weak_subjects = skill_service.get_weak_subjects(user, threshold=50)
        
        # Generate review recommendations for weak subjects
        for user_skill in weak_subjects[:3]:  # Limit to top 3 weak areas
            RecommendationService.generate_recommendation(
                user=user,
                recommendation_type='review',
                context={
                    'subject': user_skill.subject.name,
                    'current_skill': user_skill.skill_percentage,
                }
            )
        
        # Get strong subjects (above 70%)
        strong_subjects = skill_service.get_strong_subjects(user, threshold=70)
        
        # Generate advance recommendations for strong subjects
        for user_skill in strong_subjects[:2]:  # Limit to top 2 strong areas
            RecommendationService.generate_recommendation(
                user=user,
                recommendation_type='advance',
                context={
                    'subject': user_skill.subject.name,
                    'current_skill': user_skill.skill_percentage,
                }
            )
        
        # If user has no skills, suggest learning
        if not weak_subjects.exists() and not strong_subjects.exists():
            RecommendationService.generate_recommendation(
                user=user,
                recommendation_type='learn',
                context={'subject': 'n\'importe quelle matière'}
            )
    
    @staticmethod
    @transaction.atomic
    def cleanup_old_recommendations(days: int = 30):
        """
        Deactivate recommendations older than specified days.
        
        Args:
            days: Number of days after which to deactivate recommendations
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        Recommendation.objects.filter(
            created_at__lt=cutoff_date,
            is_active=True
        ).update(is_active=False)
    
    @staticmethod
    def get_similar_users(user, limit: int = 10):
        """
        Find users with similar skill profiles using cosine similarity.
        
        Args:
            user: The user to find similar users for
            limit: Maximum number of similar users to return
            
        Returns:
            List of similar users with similarity scores
        """
        # Get user's skills
        user_skills = UserSkill.objects.filter(user=user).select_related('subject')
        if not user_skills.exists():
            return []
        
        # Create skill vector for user
        user_skill_dict = {skill.subject_id: skill.skill_percentage for skill in user_skills}
        
        # Get all other users with skills
        other_users = User.objects.annotate(
            skill_count=Count('skills')
        ).filter(skill_count__gt=0).exclude(id=user.id)[:100]  # Limit to 100 users for performance
        
        similar_users = []
        
        for other_user in other_users:
            other_skills = UserSkill.objects.filter(user=other_user).select_related('subject')
            other_skill_dict = {skill.subject_id: skill.skill_percentage for skill in other_skills}
            
            # Calculate cosine similarity
            similarity = RecommendationService._calculate_cosine_similarity(
                user_skill_dict, other_skill_dict
            )
            
            if similarity > 0.3:  # Only include users with similarity > 0.3
                similar_users.append({
                    'user': other_user,
                    'similarity': similarity
                })
        
        # Sort by similarity and return top results
        similar_users.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_users[:limit]
    
    @staticmethod
    def _calculate_cosine_similarity(dict1: dict, dict2: dict) -> float:
        """
        Calculate cosine similarity between two skill dictionaries.
        
        Args:
            dict1: First skill dictionary {subject_id: skill_percentage}
            dict2: Second skill dictionary {subject_id: skill_percentage}
            
        Returns:
            float: Cosine similarity score (0-1)
        """
        # Get common subjects
        common_subjects = set(dict1.keys()) & set(dict2.keys())
        
        if not common_subjects:
            return 0.0
        
        # Calculate dot product
        dot_product = sum(dict1[subject] * dict2[subject] for subject in common_subjects)
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(dict1[subject] ** 2 for subject in dict1))
        magnitude2 = math.sqrt(sum(dict2[subject] ** 2 for subject in dict2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    @staticmethod
    @transaction.atomic
    def generate_collaborative_recommendations(user):
        """
        Generate recommendations based on what similar users found helpful.
        Uses collaborative filtering approach.
        
        Args:
            user: The user to generate recommendations for
        """
        similar_users = RecommendationService.get_similar_users(user, limit=5)
        
        if not similar_users:
            return
        
        # Get content that similar users completed successfully
        similar_user_ids = [item['user'].id for item in similar_users]
        
        # Find courses completed by similar users with high skill
        successful_courses = CourseProgress.objects.filter(
            user_id__in=similar_user_ids,
            is_completed=True
        ).values('course_id').annotate(
            completion_count=Count('id')
        ).filter(completion_count__gte=2).order_by('-completion_count')[:5]
        
        # Find TDs completed by similar users with high scores
        successful_tds = TDProgress.objects.filter(
            user_id__in=similar_user_ids,
            is_completed=True,
            score__gte=70
        ).values('td_id').annotate(
            completion_count=Count('id')
        ).filter(completion_count__gte=2).order_by('-completion_count')[:5]
        
        # Generate recommendations for courses
        for course_data in successful_courses:
            course = Course.objects.filter(id=course_data['course_id']).first()
            if course:
                # Check if user hasn't completed this course
                if not CourseProgress.objects.filter(user=user, course=course, is_completed=True).exists():
                    RecommendationService.generate_recommendation(
                        user=user,
                        recommendation_type='learn',
                        context={
                            'subject': course.subject.name,
                            'course_id': course.id,
                            'source': 'collaborative_filtering',
                            'popularity': course_data['completion_count']
                        }
                    )
        
        # Generate recommendations for TDs
        for td_data in successful_tds:
            td = TD.objects.filter(id=td_data['td_id']).first()
            if td:
                # Check if user hasn't completed this TD
                if not TDProgress.objects.filter(user=user, td=td, is_completed=True).exists():
                    RecommendationService.generate_recommendation(
                        user=user,
                        recommendation_type='practice',
                        context={
                            'subject': td.subject.name,
                            'td_id': td.id,
                            'source': 'collaborative_filtering',
                            'popularity': td_data['completion_count']
                        }
                    )
    
    @staticmethod
    @transaction.atomic
    def generate_content_based_recommendations(user):
        """
        Generate recommendations based on content similarity and user preferences.
        Uses content-based filtering approach.
        
        Args:
            user: The user to generate recommendations for
        """
        # Get user's completed content to understand preferences
        completed_courses = CourseProgress.objects.filter(
            user=user, is_completed=True
        ).select_related('course__subject')
        
        completed_tds = TDProgress.objects.filter(
            user=user, is_completed=True
        ).select_related('td__subject')
        
        # Find preferred subjects
        subject_preferences = {}
        
        for progress in completed_courses:
            subject = progress.course.subject
            subject_preferences[subject.id] = subject_preferences.get(subject.id, 0) + 1
        
        for progress in completed_tds:
            subject = progress.td.subject
            subject_preferences[subject.id] = subject_preferences.get(subject.id, 0) + 1
        
        if not subject_preferences:
            return
        
        # Get most preferred subjects
        preferred_subject_ids = sorted(subject_preferences.keys(), key=lambda x: subject_preferences[x], reverse=True)[:3]
        
        # Recommend content in preferred subjects that user hasn't completed
        for subject_id in preferred_subject_ids:
            # Recommend courses
            uncompleted_courses = Course.objects.filter(
                subject_id=subject_id,
                is_published=True
            ).exclude(
                id__in=completed_courses.values_list('course_id', flat=True)
            ).order_by('-created_at')[:2]
            
            for course in uncompleted_courses:
                RecommendationService.generate_recommendation(
                    user=user,
                    recommendation_type='learn',
                    context={
                        'subject': course.subject.name,
                        'course_id': course.id,
                        'source': 'content_based_filtering',
                        'reason': 'based_on_your_preferences'
                    }
                )
            
            # Recommend TDs
            uncompleted_tds = TD.objects.filter(
                subject_id=subject_id,
                is_published=True
            ).exclude(
                id__in=completed_tds.values_list('td_id', flat=True)
            ).order_by('-created_at')[:2]
            
            for td in uncompleted_tds:
                RecommendationService.generate_recommendation(
                    user=user,
                    recommendation_type='practice',
                    context={
                        'subject': td.subject.name,
                        'td_id': td.id,
                        'source': 'content_based_filtering',
                        'reason': 'based_on_your_preferences'
                    }
                )
    
    @staticmethod
    @transaction.atomic
    def generate_time_based_recommendations(user):
        """
        Generate recommendations based on time since last interaction.
        Suggests review of content not visited recently.
        
        Args:
            user: The user to generate recommendations for
        """
        # Find content completed more than 30 days ago
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        old_course_progress = CourseProgress.objects.filter(
            user=user,
            is_completed=True,
            completed_at__lt=thirty_days_ago
        ).select_related('course__subject')[:5]
        
        old_td_progress = TDProgress.objects.filter(
            user=user,
            is_completed=True,
            completed_at__lt=thirty_days_ago
        ).select_related('td__subject')[:5]
        
        # Generate review recommendations
        for progress in old_course_progress:
            # Check current skill in this subject
            current_skill = UserSkill.objects.filter(
                user=user,
                subject=progress.course.subject
            ).first()
            
            if current_skill and current_skill.skill_percentage < 80:
                RecommendationService.generate_recommendation(
                    user=user,
                    recommendation_type='review',
                    context={
                        'subject': progress.course.subject.name,
                        'course_id': progress.course.id,
                        'source': 'time_based',
                        'last_completed': progress.completed_at.strftime('%Y-%m-%d'),
                        'current_skill': current_skill.skill_percentage
                    }
                )
        
        for progress in old_td_progress:
            # Check current skill in this subject
            current_skill = UserSkill.objects.filter(
                user=user,
                subject=progress.td.subject
            ).first()
            
            if current_skill and current_skill.skill_percentage < 80:
                RecommendationService.generate_recommendation(
                    user=user,
                    recommendation_type='practice',
                    context={
                        'subject': progress.td.subject.name,
                        'td_id': progress.td.id,
                        'source': 'time_based',
                        'last_completed': progress.completed_at.strftime('%Y-%m-%d'),
                        'current_skill': current_skill.skill_percentage
                    }
                )
    
    @staticmethod
    @transaction.atomic
    def generate_hybrid_recommendations(user):
        """
        Generate recommendations using multiple algorithms for better personalization.
        Combines collaborative filtering, content-based filtering, and time-based approaches.
        
        Args:
            user: The user to generate recommendations for
        """
        # Clear old recommendations to avoid duplicates
        Recommendation.objects.filter(user=user, is_active=True).update(is_active=False)
        
        # Generate recommendations using different approaches
        RecommendationService.generate_recommendations_for_user(user)  # Original skill-based
        RecommendationService.generate_collaborative_recommendations(user)  # Collaborative filtering
        RecommendationService.generate_content_based_recommendations(user)  # Content-based filtering
        RecommendationService.generate_time_based_recommendations(user)  # Time-based
        
        # Keep only the highest priority recommendations (avoid overwhelming user)
        active_recommendations = Recommendation.objects.filter(
            user=user,
            is_active=True,
            is_dismissed=False
        ).order_by('-priority', '-created_at')
        
        # Keep top 10 recommendations
        if active_recommendations.count() > 10:
            to_deactivate = active_recommendations[10:]
            to_deactivate.update(is_active=False)
