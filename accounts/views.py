from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import Referral, PromoCode, PromoCodeUsage
from .services import ReferralService, PromoCodeService
from gamification.models import XPLog, UserBadge, LeaderboardEntry
from gamification.services import XPService
from skills.models import Subject, UserSkill
from skills.services import SkillService
from recommendations.services import RecommendationService
from exams.models import ExamSession
from community.models import Content, ContentPurchase


def register(request):
    """User registration view with referral code and promo code support."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        referral_code = request.POST.get('referral_code', '').strip().upper()
        promo_code = request.POST.get('promo_code', '').strip().upper()
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Process referral code if provided
            if referral_code:
                success, message, referral = ReferralService.process_referral(referral_code, user)
                if success:
                    from django.contrib import messages
                    messages.success(request, message)
                else:
                    from django.contrib import messages
                    messages.warning(request, message)
            
            # Process promo code if provided
            if promo_code:
                success, message, reward_given = PromoCodeService.apply_promo_code(user, promo_code)
                if success:
                    from django.contrib import messages
                    messages.success(request, message)
                else:
                    from django.contrib import messages
                    messages.warning(request, message)
            
            return redirect('home_authenticated')
    else:
        form = CustomUserCreationForm()
    
    # Get referral code from URL parameter
    referral_code = request.GET.get('ref', '').strip().upper()

    return render(request, 'accounts/register.html', {'form': form, 'referral_code': referral_code})


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

            return redirect('home_authenticated')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def referral_page(request):
    """
    Page de parrainage - affiche le code de parrainage et les statistiques.
    """
    user = request.user
    
    # Créer ou récupérer le code de parrainage de l'utilisateur
    referral = ReferralService.create_referral(user)
    
    # Récupérer les statistiques de parrainage
    stats = ReferralService.get_referral_stats(user)
    
    # Récupérer les parrainages effectués
    referrals_made = Referral.objects.filter(referrer=user).select_related('referred')
    
    context = {
        'referral_code': referral.referral_code,
        'stats': stats,
        'referrals_made': referrals_made,
    }
    
    return render(request, 'accounts/referral.html', context)


@login_required
@require_POST
def apply_promo_code(request):
    """
    Applique un code promo pour l'utilisateur connecté.
    """
    code = request.POST.get('promo_code', '').strip().upper()
    
    if not code:
        from django.contrib import messages
        messages.error(request, "Veuillez entrer un code promo.")
        return redirect('wallet')
    
    success, message, reward_given = PromoCodeService.apply_promo_code(request.user, code)
    
    if success:
        from django.contrib import messages
        messages.success(request, message)
    else:
        from django.contrib import messages
        messages.error(request, message)
    
    return redirect('wallet')


@login_required
def promo_codes_page(request):
    """
    Page des codes promo utilisés par l'utilisateur.
    """
    user = request.user
    
    # Récupérer les codes promo utilisés
    promo_usages = PromoCodeService.get_user_promo_usages(user)
    
    context = {
        'promo_usages': promo_usages,
    }
    
    return render(request, 'accounts/promo_codes.html', context)


@login_required
def home_authenticated(request):
    """
    Page d'accueil pour les utilisateurs connectés.
    Affiche un résumé de leur progression et des actions rapides.
    """
    user = request.user
    from gamification.models import XPLog
    from skills.models import Subject, UserSkill
    from exams.models import ExamSession
    from recommendations.services import RecommendationService

    # Récupérer les statistiques récentes
    recent_xp = XPLog.objects.filter(user=user).order_by('-created_at')[:5]
    recent_exams = ExamSession.objects.filter(user=user).order_by('-completed_at')[:5]
    
    # Récupérer les compétences
    user_skills = UserSkill.objects.filter(user=user).select_related('subject')
    
    # Récupérer les recommandations
    recommendation_service = RecommendationService()
    recommendations = recommendation_service.get_active_recommendations(user)[:3]

    context = {
        'user': user,
        'recent_xp': recent_xp,
        'recent_exams': recent_exams,
        'user_skills': user_skills,
        'recommendations': recommendations,
    }

    return render(request, 'accounts/home_authenticated.html', context)


@login_required
def dashboard(request):
    """
    Main dashboard - Learning Cockpit.
    Displays learning intelligence: XP, skills, recommendations, activity.
    """
    user = request.user
    from django.utils import timezone
    from datetime import timedelta
    from gamification.models import XPLog
    from skills.models import Subject

    # NEW: XP evolution over time (cumulative)
    today = timezone.now().date()
    xp_evolution = []
    cumulative_xp = 0
    has_xp_evolution_data = False
    for i in range(30):
        date = today - timedelta(days=29-i)
        xp_day = XPLog.objects.filter(user=user, created_at__date=date).aggregate(total=Sum('amount'))['total'] or 0
        cumulative_xp += xp_day
        if cumulative_xp > 0:
            has_xp_evolution_data = True
        xp_evolution.append({'date': date.strftime('%d/%m'), 'xp': cumulative_xp})
    
    # Only include xp_evolution if there's actual data
    if not has_xp_evolution_data:
        xp_evolution = None

    # NEW: Skill evolution over time (per subject) - only for subjects user has skills in
    skill_evolution = {}
    user_skills = UserSkill.objects.filter(user=user).select_related('subject')
    if user_skills:
        for user_skill in user_skills:
            subject = user_skill.subject
            subject_evolution = []
            current_skill = user_skill.skill_percentage
            for i in range(30):
                date = today - timedelta(days=29-i)
                # Get skill percentage at that date (simplified - would need historical tracking)
                # For now, we'll show current skill as baseline
                subject_evolution.append({
                    'date': date.strftime('%d/%m'),
                    'skill': current_skill
                })
            skill_evolution[subject.name] = subject_evolution
    else:
        skill_evolution = None

    # Get user's skills across all subjects
    skill_service = SkillService()
    user_skills = skill_service.get_user_skills(user)

    # Get recent recommendations
    recommendation_service = RecommendationService()
    recommendations = recommendation_service.get_active_recommendations(user)

    # Get recent activity (last 10) - optimisé
    recent_activity = XPLog.objects.filter(user=user).select_related('user').order_by('-created_at')[:10]

    # Get weak areas (skills below 50%)
    weak_areas = [skill for skill in user_skills if skill.skill_percentage < 50]

    # Calculate level progress
    xp_service = XPService()
    level_progress = xp_service.get_level_progress(user)

    # Get exam count by subject (optimisé avec select_related)
    exam_counts_by_subject = []
    for subject in Subject.objects.all():
        count = ExamSession.objects.filter(
            user=user,
            exam__subject=subject,
            is_completed=True
        ).select_related('exam', 'exam__subject').count()
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
        # DEBUG: Add fake data if no real data
        if xp_day == 0 and i < 5:
            xp_day = (i + 1) * 10  # Fake data for first 5 days
        xp_over_time.append({'date': date.strftime('%d/%m'), 'xp': xp_day})

    # NEW: Activity over time (last 30 days)
    activity_over_time = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        exams = ExamSession.objects.filter(user=user, started_at__date=date).count()
        # DEBUG: Add fake data if no real data
        if exams == 0 and i < 3:
            exams = 1 if i % 2 == 0 else 0  # Fake data for first 3 days
        activity_over_time.append({'date': date.strftime('%d/%m'), 'exams': exams})

    # NEW: Weekly statistics
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    xp_7d = XPLog.objects.filter(user=user, created_at__date__gte=last_7_days).aggregate(total=Sum('amount'))['total'] or 0
    xp_30d = XPLog.objects.filter(user=user, created_at__date__gte=last_30_days).aggregate(total=Sum('amount'))['total'] or 0
    exams_7d = ExamSession.objects.filter(user=user, started_at__date__gte=last_7_days).count()
    exams_30d = ExamSession.objects.filter(user=user, started_at__date__gte=last_30_days).count()

    # NEW: User badges
    user_badges = UserBadge.objects.filter(user=user).select_related('badge')

    # NEW: Leaderboard position
    leaderboard_position = LeaderboardEntry.objects.filter(
        user=user,
        leaderboard__leaderboard_type='global_xp'
    ).first()

    # NEW: Content purchases
    content_purchases = ContentPurchase.objects.filter(user=user).select_related('content')[:5]

    # NEW: User's community content - optimisé
    user_content = Content.objects.filter(author=user, status='approved').select_related('author', 'subject')[:5]

    # NEW: Study time this week
    study_time_7d = user.total_study_time_minutes  # This is total, would need weekly tracking

    # NEW: Streak visualization - semaine courante (lundi à dimanche)
    streak_data = []
    days_of_week = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    
    # Calculer le lundi de la semaine courante
    monday = today - timedelta(days=today.weekday())
    
    for i in range(7):
        date = monday + timedelta(days=i)
        # Vérifier si la date est dans le futur
        is_future = date > today
        has_activity = XPLog.objects.filter(user=user, created_at__date=date).exists()
        day_name = days_of_week[i]
        streak_data.append({
            'date': day_name, 
            'full_date': date.strftime('%d/%m'), 
            'active': has_activity,
            'is_future': is_future
        })

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
        'xp_evolution': xp_evolution,
        'skill_evolution': skill_evolution,
    }

    return render(request, 'accounts/dashboard.html', context)


@login_required
def wallet(request):
    """
    Page portefeuille — affiche le solde DC, l'historique des transactions
    et permet d'activer le Streak Shield.
    """
    from datetime import date
    from django.db.models import Sum
    from accounts.models import DCTransaction
    from accounts.services import DCService

    user = request.user
    transactions = DCTransaction.objects.filter(user=user).order_by('-created_at')[:50]

    total_earned = DCTransaction.objects.filter(
        user=user, amount__gt=0
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_spent = abs(
        DCTransaction.objects.filter(
            user=user, amount__lt=0
        ).aggregate(total=Sum('amount'))['total'] or 0
    )

    today = date.today()
    streak_shield_active = (
        user.streak_shield_active_until is not None
        and user.streak_shield_active_until >= today
    )

    context = {
        'transactions': transactions,
        'total_earned': total_earned,
        'total_spent': total_spent,
        'streak_shield_active': streak_shield_active,
    }
    return render(request, 'accounts/wallet.html', context)


@login_required
@require_POST
def streak_shield(request):
    """Active le Streak Shield pour 10 DC."""
    from django.contrib import messages
    from accounts.services import DCService

    success, message = DCService.activate_streak_shield(request.user)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect('wallet')


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

    # Get community content - optimisé
    from community.models import Content
    community_content = Content.objects.filter(author=user).select_related('author', 'subject').order_by('-created_at')

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


@login_required
def xp_evolution_api(request):
    """API endpoint for XP evolution data over time."""
    from gamification.models import XPLog
    from django.db.models import Sum
    
    user = request.user
    days = int(request.GET.get('days', 30))
    
    today = timezone.now().date()
    xp_data = []
    cumulative_xp = 0
    
    for i in range(days):
        date = today - timedelta(days=days - 1 - i)
        xp_day = XPLog.objects.filter(
            user=user,
            created_at__date=date
        ).aggregate(total=Sum('amount'))['total'] or 0
        cumulative_xp += xp_day
        xp_data.append({
            'date': date.strftime('%d/%m'),
            'xp': cumulative_xp
        })
    
    return JsonResponse({'xp_data': xp_data})


@login_required
def level_progress_api(request):
    """API endpoint for level progress."""
    user = request.user
    xp_service = XPService()
    progress = xp_service.get_level_progress(user)
    
    return JsonResponse({
        'current_level': user.level,
        'current_xp': user.total_xp,
        'xp_for_next_level': progress['xp_needed'],
        'xp_in_current_level': progress['xp_in_current_level'],
        'percentage': progress['percentage']
    })
