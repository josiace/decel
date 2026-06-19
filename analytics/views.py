from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q, F, DurationField
from django.utils import timezone
from datetime import timedelta
from .models import UserActivity, UserAnalytics
from accounts.models import User
from exams.models import ExamSession
from learning.models import CourseProgress, TDProgress
from skills.models import UserSkill
from gamification.models import UserBadge


@login_required
def user_analytics(request):
    """Show detailed analytics for the current user."""
    user = request.user
    
    # Get or create user analytics
    analytics, created = UserAnalytics.objects.get_or_create(user=user)
    
    # Calculate recent activities
    week_ago = timezone.now() - timedelta(days=7)
    month_ago = timezone.now() - timedelta(days=30)
    
    activities_this_week = UserActivity.objects.filter(
        user=user,
        created_at__gte=week_ago
    ).count()
    
    activities_this_month = UserActivity.objects.filter(
        user=user,
        created_at__gte=month_ago
    ).count()
    
    # Calculate exam statistics
    exam_sessions = ExamSession.objects.filter(user=user, is_completed=True)
    total_exams = exam_sessions.count()
    exams_passed = exam_sessions.filter(passed=True).count()
    exams_failed = total_exams - exams_passed
    avg_score = exam_sessions.aggregate(avg_score=Avg('score'))['avg_score']
    
    # Calculate content statistics
    courses_completed = CourseProgress.objects.filter(user=user, is_completed=True).count()
    tds_completed = TDProgress.objects.filter(user=user, is_completed=True).count()
    
    # Get skill statistics
    skills = UserSkill.objects.filter(user=user).select_related('subject')
    avg_skill = skills.aggregate(avg_skill=Avg('skill_percentage'))['avg_skill']
    
    # Get recent activities
    recent_activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:20]
    
    # Get activity by type (for charts)
    activity_by_type = UserActivity.objects.filter(user=user).values('activity_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Calculate study time (based on exam sessions)
    total_study_time = exam_sessions.aggregate(
        total_time=Sum(
            F('completed_at') - F('started_at'),
            output_field=DurationField()
        )
    )['total_time']
    
    if total_study_time:
        total_study_minutes = int(total_study_time.total_seconds() / 60)
    else:
        total_study_minutes = 0
    
    # Update analytics
    analytics.total_activities = UserActivity.objects.filter(user=user).count()
    analytics.activities_this_week = activities_this_week
    analytics.activities_this_month = activities_this_month
    analytics.total_exams_taken = total_exams
    analytics.exams_passed = exams_passed
    analytics.exams_failed = exams_failed
    analytics.average_exam_score = int(avg_score) if avg_score else None
    analytics.courses_completed = courses_completed
    analytics.tds_completed = tds_completed
    analytics.total_time_spent_minutes = total_study_minutes
    analytics.save()
    
    return render(request, 'analytics/user_analytics.html', {
        'analytics': analytics,
        'recent_activities': recent_activities,
        'activity_by_type': activity_by_type,
        'skills': skills,
        'avg_skill': avg_skill,
        'total_study_minutes': total_study_minutes,
    })


@login_required
def activity_log(request):
    """Show detailed activity log for the user."""
    user = request.user
    
    # Get filter parameters
    activity_type = request.GET.get('type', '')
    days = request.GET.get('days', '30')
    
    # Build query
    activities = UserActivity.objects.filter(user=user)
    
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    
    if days:
        days_ago = timezone.now() - timedelta(days=int(days))
        activities = activities.filter(created_at__gte=days_ago)
    
    activities = activities.order_by('-created_at')[:100]
    
    return render(request, 'analytics/activity_log.html', {
        'activities': activities,
        'activity_type': activity_type,
        'days': days,
    })
