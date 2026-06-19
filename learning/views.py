from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import FileResponse, Http404
from .models import Course, TD, CorrectedTD, CourseProgress, TDProgress
from .services import ContentPurchaseService
from gamification.services import XPService
from skills.services import SkillService
from recommendations.services import RecommendationService


@login_required
def course_list(request):
    """List all available courses."""
    courses = Course.objects.filter(is_published=True).select_related('subject')
    return render(request, 'learning/course_list.html', {'courses': courses})


@login_required
def course_detail(request, course_id):
    """Show course details and content."""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Check if user has completed this course
    progress, created = CourseProgress.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'is_completed': False}
    )
    
    # Check if user can access the content
    can_access = ContentPurchaseService.can_access(
        request.user,
        'course',
        course.id,
        course.dc_price
    )
    has_purchased = ContentPurchaseService.has_purchased(
        request.user,
        'course',
        course.id
    )
    
    return render(request, 'learning/course_detail.html', {
        'course': course,
        'progress': progress,
        'can_access': can_access,
        'has_purchased': has_purchased,
    })


@login_required
def course_complete(request, course_id):
    """
    Mark a course as completed.
    Awards low XP and updates skill engagement.
    """
    course = get_object_or_404(Course, id=course_id, is_published=True)
    user = request.user
    
    # Get or create progress
    progress, created = CourseProgress.objects.get_or_create(
        user=user,
        course=course,
        defaults={'is_completed': False}
    )
    
    if not progress.is_completed:
        # Mark as completed
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        
        # Award XP (low XP for course)
        xp_service = XPService()
        xp_service.award_xp(
            user=user,
            amount=XPService.XP_COURSE_READ,
            reason=f"Cours terminé : {course.title}",
            action_type='course',
            course_id=course.id
        )
        
        # Update skill (engagement metric)
        skill_service = SkillService()
        skill_service.update_skill_from_course(user, course.subject)
        
        # Generate practice recommendation
        recommendation_service = RecommendationService()
        recommendation_service.generate_recommendation(
            user=user,
            recommendation_type='practice',
            context={'subject': course.subject.name}
        )
    
    return redirect('course_detail', course_id=course.id)


@login_required
def td_list(request):
    """List all available TDs."""
    tds = TD.objects.filter(is_published=True).select_related('subject')
    return render(request, 'learning/td_list.html', {'tds': tds})


@login_required
def td_detail(request, td_id):
    """Show TD details and exercises."""
    td = get_object_or_404(TD, id=td_id, is_published=True)
    
    # Check if user has completed this TD
    progress, created = TDProgress.objects.get_or_create(
        user=request.user,
        td=td,
        defaults={'is_completed': False}
    )
    
    # Get correction if available
    try:
        correction = CorrectedTD.objects.get(td=td)
    except CorrectedTD.DoesNotExist:
        correction = None
    
    # Check if user can access the TD content
    can_access_td = ContentPurchaseService.can_access(
        request.user,
        'td',
        td.id,
        td.dc_price
    )
    
    # Check if user can access the correction
    can_access_correction = False
    if correction:
        can_access_correction = ContentPurchaseService.can_access(
            request.user,
            'corrected_td',
            correction.id,
            correction.dc_price
        )
    
    return render(request, 'learning/td_detail.html', {
        'td': td,
        'progress': progress,
        'correction': correction,
        'can_access_td': can_access_td,
        'can_access_correction': can_access_correction,
    })


@login_required
def td_complete(request, td_id):
    """
    Mark a TD as completed with a self-reported score.
    Awards medium XP and updates skills.
    """
    if request.method != 'POST':
        return redirect('td_detail', td_id=td_id)
    
    td = get_object_or_404(TD, id=td_id, is_published=True)
    user = request.user
    
    # Get score from POST
    try:
        score = int(request.POST.get('score', 0))
        score = max(0, min(100, score))  # Clamp between 0-100
    except (ValueError, TypeError):
        score = 0
    
    # Get or create progress
    progress, created = TDProgress.objects.get_or_create(
        user=user,
        td=td,
        defaults={'is_completed': False}
    )
    
    if not progress.is_completed:
        # Mark as completed
        progress.is_completed = True
        progress.score = score
        progress.completed_at = timezone.now()
        progress.save()
        
        # Award XP (medium XP for TD)
        xp_service = XPService()
        xp_service.award_xp(
            user=user,
            amount=XPService.XP_TD_COMPLETED,
            reason=f"TD terminé : {td.title}",
            action_type='td',
            td_id=td.id
        )
        
        # Update skill
        skill_service = SkillService()
        skill_service.update_skill_from_td(user, td.subject, score)
        
        # Generate recommendation based on score
        recommendation_service = RecommendationService()
        if score >= 70:
            recommendation_service.generate_recommendation(
                user=user,
                recommendation_type='advance',
                context={'subject': td.subject.name, 'td_score': score}
            )
        else:
            recommendation_service.generate_recommendation(
                user=user,
                recommendation_type='review',
                context={'subject': td.subject.name, 'td_score': score}
            )
    
    return redirect('td_detail', td_id=td.id)


@login_required
def purchase_course(request, course_id):
    """Purchase a course with XP."""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    success, message = ContentPurchaseService.purchase_content(
        request.user,
        'course',
        course.id
    )
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('course_detail', course_id=course.id)


@login_required
def purchase_td(request, td_id):
    """Purchase a TD with XP."""
    td = get_object_or_404(TD, id=td_id, is_published=True)
    
    success, message = ContentPurchaseService.purchase_content(
        request.user,
        'td',
        td.id
    )
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('td_detail', td_id=td.id)


@login_required
def purchase_correction(request, correction_id):
    """Purchase a correction with XP."""
    correction = get_object_or_404(CorrectedTD, id=correction_id)
    
    success, message = ContentPurchaseService.purchase_content(
        request.user,
        'corrected_td',
        correction.id
    )
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('td_detail', td_id=correction.td.id)


@login_required
def download_file(request, content_type, content_id):
    """Download a content file."""
    if content_type == 'course':
        content = get_object_or_404(Course, id=content_id, is_published=True)
        file_field = content.content_file
        price = content.dc_price
    elif content_type == 'td':
        content = get_object_or_404(TD, id=content_id, is_published=True)
        file_field = content.content_file
        price = content.dc_price
    elif content_type == 'corrected_td':
        content = get_object_or_404(CorrectedTD, id=content_id)
        file_field = content.correction_file
        price = content.dc_price
    else:
        raise Http404("Type de contenu invalide")
    
    # Check if user can access
    if not ContentPurchaseService.can_access(request.user, content_type, content_id, price):
        messages.error(request, "Vous devez acheter ce contenu pour le télécharger.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    if not file_field:
        raise Http404("Aucun fichier disponible")
    
    try:
        response = FileResponse(file_field.open('rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{file_field.name.split("/")[-1]}"'
        return response
    except Exception as e:
        messages.error(request, f"Erreur lors du téléchargement : {str(e)}")
        return redirect(request.META.get('HTTP_REFERER', '/'))
