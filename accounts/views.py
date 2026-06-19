from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from gamification.services import XPService
from skills.services import SkillService
from recommendations.services import RecommendationService


def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view with daily DC bonus."""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Award daily DC bonus
            from accounts.services import DCService
            success, message, transaction = DCService.award_daily_bonus(user)
            if success:
                from django.contrib import messages
                messages.success(request, message)
            
            return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def dashboard(request):
    """
    Main dashboard - Learning Cockpit.
    Displays learning intelligence: XP, skills, recommendations, activity.
    """
    user = request.user
    from django.utils import timezone
    from datetime import timedelta

    # Get user's skills across all subjects
    skill_service = SkillService()
    user_skills = skill_service.get_user_skills(user)

    # Get recent recommendations
    recommendation_service = RecommendationService()
    recommendations = recommendation_service.get_active_recommendations(user)

    # Get recent activity (last 10)
    from gamification.models import XPLog
    recent_activity = XPLog.objects.filter(user=user).order_by('-created_at')[:10]

    # Get weak areas (skills below 50%)
    weak_areas = [skill for skill in user_skills if skill.skill_percentage < 50]

    # Calculate level progress
    xp_service = XPService()
    level_progress = xp_service.get_level_progress(user)

    # Get exam count by subject
    from exams.models import ExamSession
    from skills.models import Subject
    exam_counts_by_subject = []
    for subject in Subject.objects.all():
        count = ExamSession.objects.filter(user=user, exam__subject=subject, is_completed=True).count()
        if count > 0:
            exam_counts_by_subject.append({
                'subject': subject,
                'count': count
            })

    # NEW: XP over time (last 30 days)
    today = timezone.now().date()
    xp_over_time = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        xp_day = XPLog.objects.filter(user=user, created_at__date=date).aggregate(total=Sum('amount'))['total'] or 0
        xp_over_time.append({'date': date.strftime('%Y-%m-%d'), 'xp': xp_day})

    # NEW: Activity over time (last 30 days)
    activity_over_time = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        exams = ExamSession.objects.filter(user=user, started_at__date=date).count()
        activity_over_time.append({'date': date.strftime('%Y-%m-%d'), 'exams': exams})

    # NEW: Weekly statistics
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    xp_7d = XPLog.objects.filter(user=user, created_at__date__gte=last_7_days).aggregate(total=Sum('amount'))['total'] or 0
    xp_30d = XPLog.objects.filter(user=user, created_at__date__gte=last_30_days).aggregate(total=Sum('amount'))['total'] or 0
    exams_7d = ExamSession.objects.filter(user=user, started_at__date__gte=last_7_days).count()
    exams_30d = ExamSession.objects.filter(user=user, started_at__date__gte=last_30_days).count()

    # NEW: User badges
    from gamification.models import UserBadge
    user_badges = UserBadge.objects.filter(user=user).select_related('badge')

    # NEW: Leaderboard position
    from gamification.models import LeaderboardEntry
    leaderboard_position = LeaderboardEntry.objects.filter(
        user=user,
        leaderboard__leaderboard_type='global_xp'
    ).first()

    # NEW: Content purchases
    from community.models import ContentPurchase
    content_purchases = ContentPurchase.objects.filter(user=user).select_related('content')[:5]

    # NEW: User's community content
    from community.models import Content
    user_content = Content.objects.filter(author=user, status='approved')[:5]

    # NEW: Study time this week
    study_time_7d = user.total_study_time_minutes  # This is total, would need weekly tracking

    # NEW: Streak visualization
    streak_data = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        has_activity = XPLog.objects.filter(user=user, created_at__date=date).exists()
        streak_data.append({'date': date.strftime('%d/%m'), 'active': has_activity})

    context = {
        'user': user,
        'user_skills': user_skills,
        'recommendations': recommendations,
        'recent_activity': recent_activity,
        'weak_areas': weak_areas,
        'level_progress': level_progress,
        'exam_counts_by_subject': exam_counts_by_subject,
        'xp_over_time': xp_over_time,
        'activity_over_time': activity_over_time,
        'xp_7d': xp_7d,
        'xp_30d': xp_30d,
        'exams_7d': exams_7d,
        'exams_30d': exams_30d,
        'user_badges': user_badges,
        'leaderboard_position': leaderboard_position,
        'content_purchases': content_purchases,
        'user_content': user_content,
        'study_time_7d': study_time_7d,
        'streak_data': streak_data,
    }

    return render(request, 'accounts/dashboard.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_user_detail(request, user_id):
    """
    Admin view to display all user data grouped together.
    Shows exam sessions, XP logs, DC transactions, community content, etc.
    """
    user = get_object_or_404(User, id=user_id)

    # Get exam sessions
    from exams.models import ExamSession
    exam_sessions = ExamSession.objects.filter(user=user).select_related('exam').order_by('-started_at')

    # Get XP logs
    from gamification.models import XPLog
    xp_logs = XPLog.objects.filter(user=user).order_by('-created_at')[:20]

    # Get DC transactions
    from accounts.models import DCTransaction
    dc_transactions = DCTransaction.objects.filter(user=user).order_by('-created_at')[:20]

    # Get community content
    from community.models import Content
    community_content = Content.objects.filter(author=user).order_by('-created_at')

    # Get contributor info
    from accounts.models import Contributor
    try:
        contributor = Contributor.objects.get(user=user)
    except Contributor.DoesNotExist:
        contributor = None

    context = {
        'user': user,
        'exam_sessions': exam_sessions,
        'xp_logs': xp_logs,
        'dc_transactions': dc_transactions,
        'community_content': community_content,
        'contributor': contributor,
    }

    return render(request, 'accounts/admin_user_detail.html', context)
