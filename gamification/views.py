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


def leaderboard_list(request):
    """List all available leaderboards - public pour SEO."""
    leaderboards = Leaderboard.objects.filter(is_active=True).select_related('subject')

    # Get user's current positions in each leaderboard (only if logged in)
    user_positions = {}
    if request.user.is_authenticated:
        for leaderboard in leaderboards:
            entry = leaderboard.entries.filter(user=request.user).first()
            if entry:
                user_positions[leaderboard.id] = entry.position

    return render(request, 'gamification/leaderboard_list.html', {
        'leaderboards': leaderboards,
        'user_positions': user_positions,
    })


def leaderboard_detail(request, leaderboard_id):
    """Show detailed leaderboard with rankings - public pour SEO."""
    leaderboard = get_object_or_404(Leaderboard, id=leaderboard_id, is_active=True)

    # Get entries for this leaderboard
    entries = leaderboard.entries.select_related('user').order_by('position')[:50]  # Top 50

    # Get user's position (only if logged in)
    user_entry = None
    if request.user.is_authenticated:
        user_entry = leaderboard.entries.filter(user=request.user).first()

    return render(request, 'gamification/leaderboard_detail.html', {
        'leaderboard': leaderboard,
        'entries': entries,
        'user_entry': user_entry,
    })


def global_leaderboard(request):
    """Show global XP leaderboard with detailed user information - public pour SEO."""
    # Get filter parameters
    country_filter = request.GET.get('country', '')
    grade_filter = request.GET.get('grade_level', '')
    
    # Build query
    users_query = User.objects.annotate(
        exam_count=Count('exam_sessions', filter=Q(exam_sessions__is_completed=True)),
        badge_count=Count('badges')
    )
    
    # Apply filters
    if country_filter:
        users_query = users_query.filter(country__code=country_filter)
    if grade_filter:
        users_query = users_query.filter(grade_level=grade_filter)
    
    # Get top users by XP
    top_users = users_query.select_related('country').order_by('-total_xp', '-level')[:50]
    
    # Get current user's position
    user_rank = None
    all_users = users_query.select_related('country').order_by('-total_xp', '-level')
    
    for idx, user in enumerate(all_users, 1):
        if user.id == request.user.id:
            user_rank = idx
            break
    
    # Get all countries for filter
    from accounts.models import Country
    countries = Country.objects.filter(is_active=True)
    
    return render(request, 'gamification/global_leaderboard.html', {
        'top_users': top_users,
        'user_rank': user_rank,
        'countries': countries,
        'country_filter': country_filter,
        'grade_filter': grade_filter,
    })


def subject_leaderboard(request, subject_id):
    """Show leaderboard for a specific subject based on skill percentage - public pour SEO."""
    from skills.models import Subject

    subject = get_object_or_404(Subject, id=subject_id)

    # Get filter parameters
    country_filter = request.GET.get('country', '')
    grade_filter = request.GET.get('grade_level', '')

    # Get top users by skill percentage for this subject
    skills_query = UserSkill.objects.filter(subject=subject).select_related('user')

    # Apply filters
    if country_filter:
        skills_query = skills_query.filter(user__country__code=country_filter)
    if grade_filter:
        skills_query = skills_query.filter(user__grade_level=grade_filter)

    top_skills = skills_query.order_by('-skill_percentage')[:50]

    # Get current user's skill and position (only if logged in)
    user_skill = None
    user_rank = None

    if request.user.is_authenticated:
        user_skill = UserSkill.objects.filter(user=request.user, subject=subject).first()

        all_skills = UserSkill.objects.filter(subject=subject).order_by('-skill_percentage')
        for idx, skill in enumerate(all_skills, 1):
            if skill.user_id == request.user.id:
                user_rank = idx
                break

    # Get all countries for filter
    from accounts.models import Country
    countries = Country.objects.filter(is_active=True)

    return render(request, 'gamification/subject_leaderboard.html', {
        'subject': subject,
        'top_skills': top_skills,
        'user_skill': user_skill,
        'user_rank': user_rank,
        'countries': countries,
        'country_filter': country_filter,
        'grade_filter': grade_filter,
    })
