from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from gamification.models import Leaderboard, LeaderboardEntry
from skills.models import UserSkill


class Command(BaseCommand):
    help = 'Met à jour les classements automatiquement'

    def handle(self, *args, **options):
        self.stdout.write('Mise à jour des classements...')
        
        # Types de classements
        leaderboard_types = [
            ('global_xp', 'Classement Global (XP)'),
            ('global_exams_passed', 'Examens Réussis'),
            ('global_streak', 'Streaks Actifs'),
        ]
        
        # Créer ou mettre à jour les classements globaux
        for lb_type, lb_name in leaderboard_types:
            leaderboard, created = Leaderboard.objects.get_or_create(
                leaderboard_type=lb_type,
                defaults={'name': lb_name}
            )
            
            if created:
                self.stdout.write(f'Créé: {lb_name}')
            
            # Mettre à jour les entrées
            self._update_leaderboard_entries(leaderboard, lb_type)
        
        # Créer des classements par matière
        subjects = UserSkill.objects.values_list('subject__id', 'subject__name').distinct()
        for subject_id, subject_name in subjects:
            lb_type = f'skill_{subject_id}'
            lb_name = f'Compétence: {subject_name}'
            
            leaderboard, created = Leaderboard.objects.get_or_create(
                leaderboard_type=lb_type,
                defaults={'name': lb_name}
            )
            
            if created:
                self.stdout.write(f'Créé: {lb_name}')
            
            self._update_leaderboard_entries(leaderboard, lb_type, subject_id=subject_id)
        
        self.stdout.write(self.style.SUCCESS('Classements mis à jour avec succès!'))

    def _update_leaderboard_entries(self, leaderboard, lb_type, subject_id=None):
        """Met à jour les entrées d'un classement."""
        # Supprimer les anciennes entrées
        LeaderboardEntry.objects.filter(leaderboard=leaderboard).delete()
        
        # Récupérer les utilisateurs et leurs scores
        users_data = self._get_users_data(lb_type, subject_id)
        
        # Créer les nouvelles entrées
        entries = []
        for position, (user_id, score) in enumerate(users_data, start=1):
            user = User.objects.get(id=user_id)
            entry = LeaderboardEntry(
                leaderboard=leaderboard,
                user=user,
                position=position,
                score=score
            )
            entries.append(entry)
        
        # Créer en bulk
        LeaderboardEntry.objects.bulk_create(entries)
        
        self.stdout.write(f'  {leaderboard.name}: {len(entries)} utilisateurs')

    def _get_users_data(self, lb_type, subject_id=None):
        """Récupère les données des utilisateurs pour un type de classement."""
        if lb_type == 'global_xp':
            return User.objects.filter(
                is_active=True
            ).order_by('-total_xp').values_list('id', 'total_xp')
        
        elif lb_type == 'global_exams_passed':
            from exams.models import ExamSession
            users = User.objects.filter(
                is_active=True
            ).annotate(
                exams_passed=Count('exam_sessions', filter=Q(
                    exam_sessions__score__gte=F('exam_sessions__exam__passing_score'),
                    exam_sessions__status='completed'
                ))
            ).order_by('-exams_passed')
            return [(u, u.exams_passed) for u in users]
        
        elif lb_type == 'global_streak':
            return User.objects.filter(
                is_active=True
            ).order_by('-current_streak').values_list('id', 'current_streak')
        
        elif lb_type.startswith('skill_') and subject_id:
            skills = UserSkill.objects.filter(
                subject_id=subject_id
            ).order_by('-skill_percentage').select_related('user')
            return [(skill.user, skill.skill_percentage) for skill in skills]
        
        return []
