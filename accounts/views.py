import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from analytics.models import UserExamResult, UserSkill
from analytics.utils import get_device_info, get_ip_info
from community.models import Discussion
from gamification.models import UserAchievement, UserBadge
from learning.models import Course

from .forms import (
    CountryCreateForm,
    CustomAuthenticationForm,
    CustomUserCreationForm,
    GradeLevelCreateForm,
)
from .models import (
    DCTransaction,
    PromoCode,
    PromoCodeUsage,
    Referral,
    User,
)

logger = logging.getLogger(__name__)


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Set referral cookie if exists
            referral_code = request.COOKIES.get("ref")
            if referral_code:
                try:
                    referrer = User.objects.get(referral_code=referral_code)
                    Referral.objects.create(
                        referrer=referrer,
                        referred=user,
                        ip_address=get_ip_info(request),
                        device_info=get_device_info(request),
                    )
                except User.DoesNotExist:
                    pass

            # Log user in
            login(request, user)

            # Welcome email - using template loader directly
            try:
                from django.template.loader import get_template
                template = get_template("emails/welcome.html")
                html_content = template.render({"user": user})
                subject = "Bienvenue sur DECEL!"
                msg = EmailMultiAlternatives(subject, "", "noreply@decel.com", [user.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")
                # Continue without failing the registration

            messages.success(request, "Compte créé avec succès! Bienvenue sur DECEL.")
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)

                # Check if coming from exam page
                next_url = request.GET.get("next")
                if next_url and "exam" in next_url:
                    messages.success(
                        request,
                        "Vous êtes maintenant connecté. Bonne chance pour votre examen!",
                    )
                    return redirect(next_url)

                return redirect("dashboard")
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = CustomAuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def referral_page(request):
    user = request.user

    # Get or create referral code
    referral = Referral.objects.filter(referrer=user).first()
    if not referral:
        # Create referral code if doesn't exist
        referral_code = f"DECEL-{user.id}-{user.username[:4].upper()}"
        referral = Referral.objects.create(
            referrer=user,
            referral_code=referral_code,
            reward_dc=50,
            referred_reward_dc=25
        )

    # Get referrals
    referrals = Referral.objects.filter(referrer=user)

    # Get referral stats
    total_referrals = referrals.count()
    successful_referrals = referrals.filter(referred__is_active=True).count()

    context = {
        "referral_code": referral.referral_code,
        "referral_link": f"https://decel.com/register?ref={referral.referral_code}",
        "total_referrals": total_referrals,
        "successful_referrals": successful_referrals,
    }

    return render(request, "accounts/referral.html", context)


def apply_promo_code(request):
    if request.method == "POST":
        code = request.POST.get("code").strip().upper()

        try:
            promo_code = PromoCode.objects.get(code=code, is_active=True)

            # Check if code is expired
            if promo_code.expiry_date and promo_code.expiry_date < timezone.now():
                messages.error(request, "Ce code promo est expiré.")
                return redirect("promo_codes")

            # Check if user already used this code
            if PromoCodeUsage.objects.filter(
                user=request.user, promo_code=promo_code
            ).exists():
                messages.error(request, "Vous avez déjà utilisé ce code promo.")
                return redirect("promo_codes")

            # Apply code
            user = request.user
            user.dc_balance += promo_code.amount
            user.save()

            # Record usage
            PromoCodeUsage.objects.create(
                user=user,
                promo_code=promo_code,
                ip_address=get_ip_info(request),
                device_info=get_device_info(request),
            )

            messages.success(
                request, f"Félicitations! Vous avez reçu {promo_code.amount} DC."
            )
            return redirect("promo_codes")

        except PromoCode.DoesNotExist:
            messages.error(request, "Code promo invalide.")
            return redirect("promo_codes")

    return redirect("promo_codes")


def promo_codes_page(request):
    user_codes = PromoCodeUsage.objects.filter(user=request.user).select_related(
        "promo_code"
    )

    context = {
        "user_codes": user_codes,
    }

    return render(request, "accounts/promo_codes.html", context)


def home_authenticated(request):
    # Get user's current skill levels
    user_skills = UserSkill.objects.filter(user=request.user).select_related("skill")

    # Get recommended courses
    recommended_courses = Course.objects.filter(is_published=True).order_by(
        "-created_at"
    )[:3]

    # Get recent discussions
    recent_discussions = Discussion.objects.filter(is_published=True).order_by(
        "-created_at"
    )[:5]

    context = {
        "user_skills": user_skills,
        "recommended_courses": recommended_courses,
        "recent_discussions": recent_discussions,
    }

    return render(request, "accounts/home_authenticated.html", context)


def dashboard(request):
    user = request.user

    # Get user's current skill levels with progress
    user_skills = UserSkill.objects.filter(user=user).select_related("skill")

    # Get recent exam results with optimization
    recent_results = UserExamResult.objects.filter(
        user=user
    ).select_related(
        'exam', 'exam__subject'
    ).order_by("-created_at")[:5]

    # Get streak info
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Get user's current streak
    current_streak = user.current_streak

    # Get DC balance
    dc_balance = user.dc_balance

    # Get premium status with optimization
    is_premium = user.subscriptions.filter(status='active').select_related('plan').exists()

    # Get badges with optimization
    badges = UserBadge.objects.filter(
        user=user
    ).select_related(
        'badge'
    ).prefetch_related(
        'badge__user_badges'
    )

    # Get achievements with optimization
    achievements = UserAchievement.objects.filter(user=user).select_related(
        "achievement"
    )

    context = {
        "user_skills": user_skills,
        "recent_results": recent_results,
        "current_streak": current_streak,
        "dc_balance": dc_balance,
        "is_premium": is_premium,
        "badges": badges,
        "achievements": achievements,
    }

    return render(request, "accounts/dashboard.html", context)


def wallet(request):
    user = request.user

    # Get all transactions
    transactions = DCTransaction.objects.filter(user=user).order_by("-created_at")

    # Get DC balance
    dc_balance = user.dc_balance

    context = {
        "transactions": transactions,
        "dc_balance": dc_balance,
    }

    return render(request, "accounts/wallet.html", context)


def streak_shield(request):
    from django.conf import settings
    
    user = request.user
    shield_cost = getattr(settings, 'STREAK_SHIELD_COST_DC', 100)
    shield_duration = getattr(settings, 'STREAK_SHIELD_DURATION_DAYS', 7)

    # Check if user already has an active streak shield
    active_shield = (
        user.streak_shield_active_until
        and user.streak_shield_active_until > timezone.now()
    )

    if request.method == "POST":
        if not active_shield:
            # Check if user has enough DC
            if user.dc_balance >= shield_cost:
                # Activate streak shield for configured days
                user.streak_shield_active_until = timezone.now() + timedelta(days=shield_duration)
                user.dc_balance -= shield_cost
                user.save()

                # Create transaction
                DCTransaction.objects.create(
                    user=user,
                    amount=-shield_cost,
                    transaction_type="streak_shield",
                    balance_after=user.dc_balance,
                    description=f"Activation du bouclier de streak ({shield_duration} jours)",
                )

                messages.success(request, f"Bouclier de streak activé pour {shield_duration} jours!")
                return redirect("streak_shield")
            else:
                messages.error(
                    request,
                    f"Vous n'avez pas assez de DC pour activer le bouclier de streak (coût: {shield_cost} DC).",
                )
                return redirect("streak_shield")
        else:
            messages.error(request, "Vous avez déjà un bouclier de streak actif.")
            return redirect("streak_shield")

    context = {
        "active_shield": active_shield,
        "dc_balance": user.dc_balance,
    }

    return render(request, "accounts/streak_shield.html", context)


def admin_user_detail(request, user_id):
    user = User.objects.get(pk=user_id)

    # Get user's exam results
    exam_results = UserExamResult.objects.filter(user=user).order_by("-created_at")

    # Get user's skills
    user_skills = UserSkill.objects.filter(user=user).select_related("skill")

    # Get user's transactions
    transactions = DCTransaction.objects.filter(user=user).order_by("-created_at")

    # Get user's referrals
    referrals = Referral.objects.filter(referrer=user)

    context = {
        "user": user,
        "exam_results": exam_results,
        "user_skills": user_skills,
        "transactions": transactions,
        "referrals": referrals,
    }

    return render(request, "accounts/admin_user_detail.html", context)


def xp_evolution_api(request):
    user = request.user

    # Get XP evolution over time
    xp_data = (
        UserExamResult.objects.filter(user=user)
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(total_xp=Sum("xp_earned"))
        .order_by("date")
    )

    # Prepare data for chart
    data = [
        {"date": entry["date"].strftime("%Y-%m-%d"), "xp": entry["total_xp"]}
        for entry in xp_data
    ]

    return JsonResponse(data, safe=False)


def level_progress_api(request):
    user = request.user

    # Get level progress
    user_skills = UserSkill.objects.filter(user=user).select_related('subject')

    data = [
        {
            "subject": skill.subject.name,
            "skill_percentage": skill.skill_percentage,
            "total_exams_taken": skill.total_exams_taken,
            "total_td_completed": skill.total_td_completed,
            "total_courses_read": skill.total_courses_read,
        }
        for skill in user_skills
    ]

    return JsonResponse(data, safe=False)


def country_create(request):
    if request.method == "POST":
        form = CountryCreateForm(request.POST)
        if form.is_valid():
            country = form.save(commit=False)
            country.created_by = request.user
            country.save()
            messages.success(request, "Pays créé avec succès!")
            return redirect("country_create")
    else:
        form = CountryCreateForm()

    return render(request, "accounts/country_create.html", {"form": form})


def grade_level_create(request):
    if request.method == "POST":
        form = GradeLevelCreateForm(request.POST)
        if form.is_valid():
            grade_level = form.save(commit=False)
            grade_level.created_by = request.user
            grade_level.save()
            messages.success(request, "Niveau scolaire créé avec succès!")
            return redirect("grade_level_create")
    else:
        form = GradeLevelCreateForm()

    return render(request, "accounts/grade_level_create.html", {"form": form})


def visitor_statistics(request):
    from analytics.models import VisitorTracking

    # Get visitor statistics
    visitors = VisitorTracking.objects.all()

    # Get stats by country
    country_stats = (
        visitors.values("country__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    # Get stats by device type
    device_stats = (
        visitors.values("device_type").annotate(count=Count("id")).order_by("-count")
    )

    # Get stats over time
    time_stats = (
        visitors.annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    context = {
        "country_stats": country_stats,
        "device_stats": device_stats,
        "time_stats": time_stats,
    }

    return render(request, "accounts/visitor_statistics.html", context)


def profile(request):
    return render(request, "accounts/profile.html")
