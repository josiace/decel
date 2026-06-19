from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Leaderboard, LeaderboardEntry
from accounts.models import User
from skills.models import UserSkill
from exams.models import ExamSession
from gamification.models import UserBadge


@login_required
def leaderboard_list(request):
    """List all available leaderboards."""
    leaderboards = Leaderboard.objects.filter(is_active=True).select_related('subject')
    
    # Get user's current positions in each leaderboard
    user_positions = {}
    for leaderboard in leaderboards:
        entry = leaderboard.entries.filter(user=request.user).first()
        if entry:
            user_positions[leaderboard.id] = entry.position
    
    return render(request, 'gamification/leaderboard_list.html', {
        'leaderboards': leaderboards,
        'user_positions': user_positions,
    })


@login_required
def leaderboard_detail(request, leaderboard_id):
    """Show detailed leaderboard with rankings."""
    leaderboard = get_object_or_404(Leaderboard, id=leaderboard_id, is_active=True)
    
    # Get entries for this leaderboard
    entries = leaderboard.entries.select_related('user').order_by('position')[:50]  # Top 50
    
    # Get user's position
    user_entry = leaderboard.entries.filter(user=request.user).first()
    
    return render(request, 'gamification/leaderboard_detail.html', {
        'leaderboard': leaderboard,
        'entries': entries,
        'user_entry': user_entry,
    })


@login_required
def global_leaderboard(request):
    """Show global XP leaderboard."""
    # Get top users by XP
    top_users = User.objects.annotate(
        exam_count=Count('exam_sessions', filter=Q(exam_sessions__is_completed=True)),
        badge_count=Count('badges')
    ).order_by('-total_xp', '-level')[:50]
    
    # Get current user's position
    user_rank = None
    all_users = User.objects.annotate(
        exam_count=Count('exam_sessions', filter=Q(exam_sessions__is_completed=True)),
        badge_count=Count('badges')
    ).order_by('-total_xp', '-level')
    
    for idx, user in enumerate(all_users, 1):
        if user.id == request.user.id:
            user_rank = idx
            break
    
    return render(request, 'gamification/global_leaderboard.html', {
        'top_users': top_users,
        'user_rank': user_rank,
    })


@login_required
def subject_leaderboard(request, subject_id):
    """Show leaderboard for a specific subject based on skill percentage."""
    from skills.models import Subject
    
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Get top users by skill percentage for this subject
    top_skills = UserSkill.objects.filter(
        subject=subject
    ).select_related('user').order_by('-skill_percentage')[:50]
    
    # Get current user's skill and position
    user_skill = UserSkill.objects.filter(user=request.user, subject=subject).first()
    user_rank = None
    
    all_skills = UserSkill.objects.filter(subject=subject).order_by('-skill_percentage')
    for idx, skill in enumerate(all_skills, 1):
        if skill.user_id == request.user.id:
            user_rank = idx
            break
    
    return render(request, 'gamification/subject_leaderboard.html', {
        'subject': subject,
        'top_skills': top_skills,
        'user_skill': user_skill,
        'user_rank': user_rank,
    })
