from django.db import transaction
from django.utils import timezone
from .models import Recommendation
from skills.services import SkillService
from datetime import timedelta


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
