from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Avg, Sum, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from exams.models import ExamSession
from gamification.models import XPLog
from community.models import Content, ContentPurchase
from learning.models import Course, TD
from .models import PageView, ClickEvent, UserSession


def is_staff_user(user):
    """Check if user is staff."""
    return user.is_staff


@user_passes_test(is_staff_user)
def admin_analytics_dashboard(request):
    """
    Admin analytics dashboard with charts and statistics.
    Shows user growth, exam performance, revenue, etc.
    """
    # Time periods
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    last_90_days = today - timedelta(days=90)

    # User statistics
    total_users = User.objects.count()
    new_users_7d = User.objects.filter(date_joined__date__gte=last_7_days).count()
    new_users_30d = User.objects.filter(date_joined__date__gte=last_30_days).count()
    active_users_30d = User.objects.filter(last_login__date__gte=last_30_days).count()

    # Exam statistics
    total_exams = ExamSession.objects.count()
    exams_7d = ExamSession.objects.filter(started_at__date__gte=last_7_days).count()
    exams_30d = ExamSession.objects.filter(started_at__date__gte=last_30_days).count()
    avg_score = ExamSession.objects.filter(score__isnull=False).aggregate(avg=Avg('score'))['avg'] or 0
    passed_exams = ExamSession.objects.filter(passed=True).count()
    pass_rate = (passed_exams / total_exams * 100) if total_exams > 0 else 0

    # XP statistics
    total_xp_awarded = XPLog.objects.aggregate(total=Sum('amount'))['total'] or 0
    xp_7d = XPLog.objects.filter(created_at__date__gte=last_7_days).aggregate(total=Sum('amount'))['total'] or 0
    xp_30d = XPLog.objects.filter(created_at__date__gte=last_30_days).aggregate(total=Sum('amount'))['total'] or 0

    # Content statistics
    total_content = Content.objects.filter(status='approved').count()
    content_purchases = ContentPurchase.objects.count()
    revenue_7d = ContentPurchase.objects.filter(purchased_at__date__gte=last_7_days).aggregate(total=Sum('price_paid'))['total'] or 0
    revenue_30d = ContentPurchase.objects.filter(purchased_at__date__gte=last_30_days).aggregate(total=Sum('price_paid'))['total'] or 0

    # Course and TD statistics
    total_courses = Course.objects.count()
    total_tds = TD.objects.count()

    # User growth over time (last 30 days)
    user_growth = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        count = User.objects.filter(date_joined__date__lte=date).count()
        user_growth.append({'date': date.strftime('%Y-%m-%d'), 'count': count})

    # Exam completion over time (last 30 days)
    exam_completion = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        count = ExamSession.objects.filter(started_at__date=date).count()
        exam_completion.append({'date': date.strftime('%Y-%m-%d'), 'count': count})

    # XP earned over time (last 30 days)
    xp_earned = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        total = XPLog.objects.filter(created_at__date=date).aggregate(total=Sum('amount'))['total'] or 0
        xp_earned.append({'date': date.strftime('%Y-%m-%d'), 'amount': total})

    # Revenue over time (last 30 days)
    revenue_over_time = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        total = ContentPurchase.objects.filter(purchased_at__date=date).aggregate(total=Sum('price_paid'))['total'] or 0
        revenue_over_time.append({'date': date.strftime('%Y-%m-%d'), 'amount': total})

    # Top performers by XP
    top_performers = User.objects.order_by('-total_xp')[:10]

    # Most popular content
    popular_content = Content.objects.annotate(
        purchase_count=Count('purchases')
    ).filter(status='approved').order_by('-purchase_count')[:10]

    # Exam pass rate by subject
    from skills.models import Subject
    subject_performance = []
    for subject in Subject.objects.all():
        sessions = ExamSession.objects.filter(exam__subject=subject, passed=True).count()
        total = ExamSession.objects.filter(exam__subject=subject).count()
        rate = (sessions / total * 100) if total > 0 else 0
        subject_performance.append({
            'subject': subject.name,
            'pass_rate': rate,
            'total_exams': total
        })

    # User level distribution
    level_distribution = []
    for level in range(1, 11):
        count = User.objects.filter(level=level).count()
        level_distribution.append({'level': f'Niveau {level}', 'count': count})

    # Page views analytics
    total_page_views = PageView.objects.count()
    page_views_7d = PageView.objects.filter(created_at__date__gte=last_7_days).count()
    page_views_30d = PageView.objects.filter(created_at__date__gte=last_30_days).count()

    # Page views over time (last 30 days)
    page_views_over_time = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        count = PageView.objects.filter(created_at__date=date).count()
        page_views_over_time.append({'date': date.strftime('%Y-%m-%d'), 'count': count})

    # Top pages by views
    top_pages = PageView.objects.values('url').annotate(
        views=Count('id')
    ).order_by('-views')[:10]

    # Device distribution
    device_distribution = PageView.objects.values('device_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # Click analytics
    total_clicks = ClickEvent.objects.count()
    clicks_7d = ClickEvent.objects.filter(created_at__date__gte=last_7_days).count()
    clicks_30d = ClickEvent.objects.filter(created_at__date__gte=last_30_days).count()

    # Clicks over time (last 30 days)
    clicks_over_time = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        count = ClickEvent.objects.filter(created_at__date=date).count()
        clicks_over_time.append({'date': date.strftime('%Y-%m-%d'), 'count': count})

    # Session analytics
    total_sessions = UserSession.objects.count()
    sessions_7d = UserSession.objects.filter(start_time__date__gte=last_7_days).count()
    sessions_30d = UserSession.objects.filter(start_time__date__gte=last_30_days).count()
    avg_session_duration = UserSession.objects.aggregate(
        avg=Avg('duration_seconds')
    )['avg'] or 0

    # Sessions over time (last 30 days)
    sessions_over_time = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        count = UserSession.objects.filter(start_time__date=date).count()
        sessions_over_time.append({'date': date.strftime('%Y-%m-%d'), 'count': count})

    # Daily activity (logins, exams, purchases) - last 30 days
    daily_activity = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        logins = User.objects.filter(last_login__date=date).count()
        exams = ExamSession.objects.filter(started_at__date=date).count()
        purchases = ContentPurchase.objects.filter(purchased_at__date=date).count()
        daily_activity.append({
            'date': date.strftime('%Y-%m-%d'),
            'logins': logins,
            'exams': exams,
            'purchases': purchases
        })

    # Content type distribution
    content_type_distribution = []
    for content_type in ['course', 'td', 'article', 'video', 'quiz']:
        count = Content.objects.filter(content_type=content_type, status='approved').count()
        content_type_distribution.append({
            'type': content_type,
            'count': count
        })

    # Contributor performance
    from accounts.models import Contributor
    contributor_performance = []
    for contributor in Contributor.objects.filter(is_active=True):
        content_count = Content.objects.filter(author=contributor.user, status='approved').count()
        exam_count = ExamSession.objects.filter(exam__created_by=contributor.user).count()
        contributor_performance.append({
            'email': contributor.user.email,
            'content_count': content_count,
            'exam_count': exam_count
        })

    # Engagement trends (streaks, study time)
    avg_streak = User.objects.aggregate(avg=Avg('current_streak'))['avg'] or 0
    avg_study_time = User.objects.aggregate(avg=Avg('total_study_time_minutes'))['avg'] or 0

    # Weekly engagement (last 7 weeks)
    weekly_engagement = []
    for i in range(7):
        week_start = today - timedelta(days=(i+1)*7)
        week_end = today - timedelta(days=i*7)
        xp_week = XPLog.objects.filter(created_at__date__range=[week_start, week_end]).aggregate(total=Sum('amount'))['total'] or 0
        weekly_engagement.append({
            'week': f'Semaine {7-i}',
            'xp': xp_week
        })

    # Real-time activity (last 24 hours by hour)
    hourly_activity = []
    for i in range(24):
        hour = (timezone.now() - timedelta(hours=i)).hour
        date = (timezone.now() - timedelta(hours=i)).date()
        logins = User.objects.filter(last_login__date=date, last_login__hour=hour).count()
        exams = ExamSession.objects.filter(started_at__date=date, started_at__hour=hour).count()
        hourly_activity.append({
            'hour': f'{hour}:00',
            'logins': logins,
            'exams': exams
        })
    hourly_activity.reverse()

    # Conversion funnel (registration → first activity)
    registered_users = User.objects.all()
    users_with_xp = User.objects.filter(total_xp__gt=0).count()
    users_with_exams = User.objects.filter(exam_session__isnull=False).distinct().count()
    users_with_purchases = User.objects.filter(community_content_purchases__isnull=False).distinct().count()

    conversion_funnel = [
        {'stage': 'Inscriptions', 'count': registered_users.count()},
        {'stage': 'Première activité (XP)', 'count': users_with_xp},
        {'stage': 'Premier examen', 'count': users_with_exams},
        {'stage': 'Premier achat', 'count': users_with_purchases},
    ]

    # Retention (users active over time)
    retention_data = []
    for i in range(12):
        month_start = today - timedelta(days=30*(i+1))
        month_end = today - timedelta(days=30*i)
        active_users = User.objects.filter(
            last_login__date__range=[month_start, month_end]
        ).count()
        retention_data.append({
            'month': f'Mois {12-i}',
            'active_users': active_users
        })
    retention_data.reverse()

    # Content creation trends
    content_creation = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        created = Content.objects.filter(created_at__date=date).count()
        content_creation.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': created
        })

    # Exam success rate over time
    exam_success_rate = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        sessions = ExamSession.objects.filter(started_at__date=date)
        total = sessions.count()
        passed = sessions.filter(passed=True).count()
        rate = (passed / total * 100) if total > 0 else 0
        exam_success_rate.append({
            'date': date.strftime('%Y-%m-%d'),
            'rate': rate
        })

    # Geographic distribution
    geo_distribution = []
    for country in Country.objects.all()[:10]:
        user_count = User.objects.filter(country=country).count()
        if user_count > 0:
            geo_distribution.append({
                'country': country.name,
                'count': user_count
            })

    context = {
        'user_stats': {
            'total': total_users,
            'new_7d': new_users_7d,
            'new_30d': new_users_30d,
            'active_30d': active_users_30d,
        },
        'exam_stats': {
            'total': total_exams,
            'exams_7d': exams_7d,
            'exams_30d': exams_30d,
            'avg_score': round(avg_score, 1),
            'pass_rate': round(pass_rate, 1),
        },
        'xp_stats': {
            'total': total_xp_awarded,
            'xp_7d': xp_7d,
            'xp_30d': xp_30d,
        },
        'content_stats': {
            'total': total_content,
            'purchases': content_purchases,
            'revenue_7d': revenue_7d,
            'revenue_30d': revenue_30d,
        },
        'learning_stats': {
            'courses': total_courses,
            'tds': total_tds,
        },
        'engagement_stats': {
            'avg_streak': round(avg_streak, 1),
            'avg_study_time': round(avg_study_time, 1),
        },
        # New analytics tracking data
        'total_page_views': total_page_views,
        'page_views_7d': page_views_7d,
        'page_views_30d': page_views_30d,
        'total_clicks': total_clicks,
        'clicks_7d': clicks_7d,
        'clicks_30d': clicks_30d,
        'total_sessions': total_sessions,
        'sessions_7d': sessions_7d,
        'sessions_30d': sessions_30d,
        'avg_session_duration': round(avg_session_duration / 60, 1) if avg_session_duration else 0,
        'user_growth': user_growth,
        'exam_completion': exam_completion,
        'xp_earned': xp_earned,
        'revenue_over_time': revenue_over_time,
        'top_performers': top_performers,
        'popular_content': popular_content,
        'subject_performance': subject_performance,
        'level_distribution': level_distribution,
        'daily_activity': daily_activity,
        'content_type_distribution': content_type_distribution,
        'contributor_performance': contributor_performance,
        'weekly_engagement': weekly_engagement,
        'hourly_activity': hourly_activity,
        'conversion_funnel': conversion_funnel,
        'retention_data': retention_data,
        'content_creation': content_creation,
        'exam_success_rate': exam_success_rate,
        'geo_distribution': geo_distribution,
        # New analytics chart data
        'page_views_over_time': page_views_over_time,
        'top_pages': top_pages,
        'device_distribution': device_distribution,
        'clicks_over_time': clicks_over_time,
        'sessions_over_time': sessions_over_time,
    }

    return render(request, 'analytics/admin_dashboard.html', context)


@user_passes_test(is_staff_user)
def admin_user_analytics(request, user_id):
    """
    Admin analytics dashboard for a specific user.
    Shows user-specific charts and statistics.
    """
    user = get_object_or_404(User, id=user_id)

    # Time periods
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)

    # User statistics
    user_xp_logs = XPLog.objects.filter(user=user)
    total_xp = user_xp_logs.aggregate(total=Sum('amount'))['total'] or 0
    xp_7d = user_xp_logs.filter(created_at__date__gte=last_7_days).aggregate(total=Sum('amount'))['total'] or 0
    xp_30d = user_xp_logs.filter(created_at__date__gte=last_30_days).aggregate(total=Sum('amount'))['total'] or 0

    # Exam statistics
    user_sessions = ExamSession.objects.filter(user=user)
    total_exams = user_sessions.count()
    exams_7d = user_sessions.filter(started_at__date__gte=last_7_days).count()
    exams_30d = user_sessions.filter(started_at__date__gte=last_30_days).count()
    passed_exams = user_sessions.filter(passed=True).count()
    avg_score = user_sessions.filter(score__isnull=False).aggregate(avg=Avg('score'))['avg'] or 0
    pass_rate = (passed_exams / total_exams * 100) if total_exams > 0 else 0

    # Content purchases
    user_purchases = ContentPurchase.objects.filter(user=user)
    total_purchases = user_purchases.count()
    purchases_7d = user_purchases.filter(purchased_at__date__gte=last_7_days).count()
    purchases_30d = user_purchases.filter(purchased_at__date__gte=last_30_days).count()
    total_spent = user_purchases.aggregate(total=Sum('price_paid'))['total'] or 0

    # XP earned over time (last 30 days)
    xp_over_time = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        total = user_xp_logs.filter(created_at__date=date).aggregate(total=Sum('amount'))['total'] or 0
        xp_over_time.append({'date': date.strftime('%Y-%m-%d'), 'amount': total})

    # Exam performance over time (last 30 days)
    exam_performance = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        sessions = user_sessions.filter(started_at__date=date)
        count = sessions.count()
        avg = sessions.filter(score__isnull=False).aggregate(avg=Avg('score'))['avg'] or 0
        exam_performance.append({'date': date.strftime('%Y-%m-%d'), 'count': count, 'avg_score': avg})

    # XP by action type
    xp_by_action = []
    for action_type in ['exam', 'td', 'course', 'login']:
        total = user_xp_logs.filter(action_type=action_type).aggregate(total=Sum('amount'))['total'] or 0
        xp_by_action.append({'action': action_type, 'amount': total})

    # Subject performance
    from skills.models import Subject
    from skills.models import UserSkill
    subject_performance = []
    for subject in Subject.objects.all():
        user_skill = UserSkill.objects.filter(user=user, subject=subject).first()
        if user_skill:
            subject_performance.append({
                'subject': subject.name,
                'skill_percentage': user_skill.skill_percentage
            })

    # Recent activity
    recent_xp_logs = user_xp_logs.order_by('-created_at')[:10]
    recent_exams = user_sessions.order_by('-started_at')[:10]

    context = {
        'user': user,
        'xp_stats': {
            'total': total_xp,
            'xp_7d': xp_7d,
            'xp_30d': xp_30d,
        },
        'exam_stats': {
            'total': total_exams,
            'exams_7d': exams_7d,
            'exams_30d': exams_30d,
            'avg_score': round(avg_score, 1),
            'pass_rate': round(pass_rate, 1),
            'passed': passed_exams,
        },
        'purchase_stats': {
            'total': total_purchases,
            'purchases_7d': purchases_7d,
            'purchases_30d': purchases_30d,
            'total_spent': total_spent,
        },
        'xp_over_time': xp_over_time,
        'exam_performance': exam_performance,
        'xp_by_action': xp_by_action,
        'subject_performance': subject_performance,
        'recent_xp_logs': recent_xp_logs,
        'recent_exams': recent_exams,
    }

    return render(request, 'analytics/admin_user_analytics.html', context)
