from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
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
    """User login view."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def dashboard(request):
    """
    Main dashboard - Learning Cockpit.
    Displays learning intelligence: XP, skills, recommendations, activity.
    """
    user = request.user
    
    # Get user's skills across all subjects
    skill_service = SkillService()
    user_skills = skill_service.get_user_skills(user)
    
    # Get recent recommendations
    recommendation_service = RecommendationService()
    recommendations = recommendation_service.get_active_recommendations(user)
    
    # Get recent activity (last 5)
    from gamification.models import XPLog
    recent_activity = XPLog.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Get weak areas (skills below 50%)
    weak_areas = [skill for skill in user_skills if skill.skill_percentage < 50]
    
    # Calculate level progress
    xp_service = XPService()
    level_progress = xp_service.get_level_progress(user)
    
    context = {
        'user': user,
        'user_skills': user_skills,
        'recommendations': recommendations,
        'recent_activity': recent_activity,
        'weak_areas': weak_areas,
        'level_progress': level_progress,
    }
    
    return render(request, 'accounts/dashboard.html', context)
