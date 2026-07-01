from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.http import FileResponse, Http404, JsonResponse
from django.db.models import Q, Avg
from .models import Course, TD, CorrectedTD, CourseProgress, TDProgress, Review
from .services import ContentPurchaseService, ContentVersionService
from .forms import CourseCreateForm, CourseUpdateForm, TDCreateForm, TDUpdateForm, CorrectedTDCreateForm, CorrectedTDUpdateForm
from gamification.services import XPService
from skills.services import SkillService
from skills.models import Subject
from recommendations.services import RecommendationService


@login_required
def course_list(request):
    """List all available courses with advanced search."""
    courses = Course.objects.filter(is_published=True).select_related('subject')
    subjects = Subject.objects.all()
    
    # Search query
    q = request.GET.get('q', '')
    if q:
        courses = courses.filter(
            Q(title__icontains=q) | 
            Q(description__icontains=q)
        )
    
    # Filter by subject
    subject_id = request.GET.get('subject', '')
    if subject_id:
        courses = courses.filter(subject_id=subject_id)
    
    # Filter by content type
    content_type = request.GET.get('content_type', '')
    if content_type:
        courses = courses.filter(content_type=content_type)
    
    # Filter by price
    price_filter = request.GET.get('price', '')
    if price_filter == 'free':
        courses = courses.filter(dc_price=0)
    elif price_filter == 'paid':
        courses = courses.filter(dc_price__gt=0)
    
    # Filter by country
    country_filter = request.GET.get('country', '')
    if country_filter:
        courses = courses.filter(country=country_filter)
    
    # Filter by grade level
    grade_filter = request.GET.get('grade_level', '')
    if grade_filter:
        courses = courses.filter(grade_level=grade_filter)
    
    context = {
        'courses': courses,
        'subjects': subjects,
        'meta_description': 'Explorez nos cours en ligne gratuits et payants. Mathématiques, Physique, Chimie et plus. Apprenez à votre rythme avec DECEL et gagnez des XP.',
        'meta_keywords': 'cours en ligne, apprentissage, éducation, DECEL, cours gratuits, Mathématiques, Physique, Chimie, études en ligne',
    }
    return render(request, 'learning/course_list.html', context)


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
    
    # Get reviews for this course
    reviews = Review.objects.filter(
        content_type='course',
        course=course,
        is_approved=True
    ).select_related('user').order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Check if user has already reviewed
    user_review = Review.objects.filter(
        content_type='course',
        course=course,
        user=request.user
    ).first()
    
    context = {
        'course': course,
        'progress': progress,
        'can_access': can_access,
        'has_purchased': has_purchased,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_review': user_review,
        'meta_description': f"Cours : {course.title} en {course.subject.name}. {course.description[:150] if course.description else 'Apprenez à votre rythme avec ce cours interactif.'} Prix : {course.dc_price} DC.",
        'meta_keywords': f"{course.subject.name}, cours en ligne, {course.title}, apprentissage, DECEL, {course.subject.name} cours",
    }
    return render(request, 'learning/course_detail.html', context)


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
    """List all available TDs with advanced search."""
    tds = TD.objects.filter(is_published=True).select_related('subject')
    subjects = Subject.objects.all()
    
    # Search query
    q = request.GET.get('q', '')
    if q:
        tds = tds.filter(
            Q(title__icontains=q) | 
            Q(description__icontains=q)
        )
    
    # Filter by subject
    subject_id = request.GET.get('subject', '')
    if subject_id:
        tds = tds.filter(subject_id=subject_id)
    
    # Filter by content type
    content_type = request.GET.get('content_type', '')
    if content_type:
        tds = tds.filter(content_type=content_type)
    
    # Filter by price
    price_filter = request.GET.get('price', '')
    if price_filter == 'free':
        tds = tds.filter(dc_price=0)
    elif price_filter == 'paid':
        tds = tds.filter(dc_price__gt=0)
    
    # Filter by country
    country_filter = request.GET.get('country', '')
    if country_filter:
        tds = tds.filter(country=country_filter)
    
    # Filter by grade level
    grade_filter = request.GET.get('grade_level', '')
    if grade_filter:
        tds = tds.filter(grade_level=grade_filter)
    
    context = {
        'tds': tds,
        'subjects': subjects,
        'meta_description': 'Pratiquez avec nos TD (Travaux Dirigés) corrigés et non corrigés. Mathématiques, Physique, Chimie et plus. Exercices pour améliorer vos compétences sur DECEL.',
        'meta_keywords': 'TD, travaux dirigés, exercices corrigés, pratique, DECEL, exercices mathématiques, exercices physique',
    }
    return render(request, 'learning/td_list.html', context)


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
    
    context = {
        'td': td,
        'progress': progress,
        'correction': correction,
        'can_access_td': can_access_td,
        'can_access_correction': can_access_correction,
        'meta_description': f"TD : {td.title} en {td.subject.name}. {td.description[:150] if td.description else 'Pratiquez avec ces exercices interactifs.'} Prix : {td.dc_price} DC.",
        'meta_keywords': f"{td.subject.name}, TD, travaux dirigés, {td.title}, exercices, DECEL, {td.subject.name} exercices",
    }
    return render(request, 'learning/td_detail.html', context)


@login_required
def td_complete(request, td_id):
    """
    Mark a TD as completed without requiring a score.
    Awards medium XP and updates skills with a default score.
    """
    if request.method != 'POST':
        return redirect('td_detail', td_id=td_id)
    
    td = get_object_or_404(TD, id=td_id, is_published=True)
    user = request.user
    
    # Default score for completion (no self-evaluation)
    score = 50  # Default score for completion
    
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
        
        # Update skill with default score
        skill_service = SkillService()
        skill_service.update_skill_from_td(user, td.subject, score)
        
        # Generate practice recommendation (since no score to base on)
        recommendation_service = RecommendationService()
        recommendation_service.generate_recommendation(
            user=user,
            recommendation_type='practice',
            context={'subject': td.subject.name}
        )
    
    return redirect('td_detail', td_id=td.id)


@login_required
def purchase_course(request, course_id):
    """Purchase a course with DC."""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    promo_code = request.POST.get('promo_code', '').strip() if request.method == 'POST' else None
    
    success, message = ContentPurchaseService.purchase_content(
        request.user,
        'course',
        course.id,
        promo_code=promo_code
    )
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('course_detail', course_id=course.id)


@login_required
def purchase_td(request, td_id):
    """Purchase a TD with DC."""
    td = get_object_or_404(TD, id=td_id, is_published=True)
    
    promo_code = request.POST.get('promo_code', '').strip() if request.method == 'POST' else None
    
    success, message = ContentPurchaseService.purchase_content(
        request.user,
        'td',
        td.id,
        promo_code=promo_code
    )
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('td_detail', td_id=td.id)


@login_required
def purchase_correction(request, correction_id):
    """Purchase a correction with DC."""
    correction = get_object_or_404(CorrectedTD, id=correction_id)
    
    promo_code = request.POST.get('promo_code', '').strip() if request.method == 'POST' else None
    
    success, message = ContentPurchaseService.purchase_content(
        request.user,
        'corrected_td',
        correction.id,
        promo_code=promo_code
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


@login_required
def content_version_history(request, content_type, content_id):
    """Affiche l'historique des versions d'un contenu."""
    if content_type == 'course':
        content = get_object_or_404(Course, id=content_id)
    elif content_type == 'td':
        content = get_object_or_404(TD, id=content_id)
    elif content_type == 'corrected_td':
        content = get_object_or_404(CorrectedTD, id=content_id)
    else:
        raise Http404("Type de contenu invalide")
    
    # Vérifier que l'utilisateur est l'auteur ou admin
    if content.author != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission de voir l'historique.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    versions = ContentVersionService.get_version_history(content)
    
    context = {
        'content': content,
        'content_type': content_type,
        'versions': versions,
    }
    return render(request, 'learning/version_history.html', context)


@login_required
@require_POST
def submit_review(request):
    """Submit a review for content."""
    content_type = request.POST.get('content_type')
    content_id = request.POST.get('content_id')
    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '')
    
    if not content_type or not content_id or not rating:
        return JsonResponse({'success': False, 'error': 'Données manquantes'})
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return JsonResponse({'success': False, 'error': 'Note invalide (1-5)'})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Note invalide'})
    
    # Get the content object
    if content_type == 'course':
        content = get_object_or_404(Course, id=content_id, is_published=True)
        review, created = Review.objects.get_or_create(
            user=request.user,
            content_type='course',
            course=content,
            td=None,
            corrected_td=None,
            defaults={'rating': rating, 'comment': comment}
        )
        if not created:
            review.rating = rating
            review.comment = comment
            review.save()
    elif content_type == 'td':
        content = get_object_or_404(TD, id=content_id, is_published=True)
        review, created = Review.objects.get_or_create(
            user=request.user,
            content_type='td',
            course=None,
            td=content,
            corrected_td=None,
            defaults={'rating': rating, 'comment': comment}
        )
        if not created:
            review.rating = rating
            review.comment = comment
            review.save()
    else:
        return JsonResponse({'success': False, 'error': 'Type de contenu invalide'})
    
    return JsonResponse({'success': True, 'message': 'Avis soumis avec succès'})


@login_required
def restore_content_version(request, content_type, content_id, version_number):
    """Restaure une version précédente d'un contenu."""
    if content_type == 'course':
        content = get_object_or_404(Course, id=content_id)
    elif content_type == 'td':
        content = get_object_or_404(TD, id=content_id)
    elif content_type == 'corrected_td':
        content = get_object_or_404(CorrectedTD, id=content_id)
    else:
        raise Http404("Type de contenu invalide")
    
    # Vérifier que l'utilisateur est l'auteur ou admin
    if content.author != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission de restaurer cette version.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    success, message = ContentVersionService.restore_version(
        content, version_number, request.user
    )
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('content_version_history', content_type=content_type, content_id=content_id)


# Contributor Views for Content Creation
@login_required
def course_create(request):
    """Créer un nouveau cours (pour contributeurs)."""
    if not request.user.is_contributor and not request.user.is_staff:
        messages.error(request, "Vous devez être contributeur pour créer un cours.")
        return redirect('course_list')
    
    if request.method == 'POST':
        form = CourseCreateForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user
            course.save()
            messages.success(request, "Cours créé avec succès!")
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseCreateForm()
    
    return render(request, 'learning/course_form.html', {'form': form, 'title': 'Créer un cours'})


@login_required
def course_update(request, course_id):
    """Modifier un cours existant (pour contributeurs)."""
    course = get_object_or_404(Course, id=course_id)
    
    if course.author != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission de modifier ce cours.")
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        form = CourseUpdateForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Cours modifié avec succès!")
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseUpdateForm(instance=course)
    
    return render(request, 'learning/course_form.html', {'form': form, 'title': 'Modifier le cours', 'course': course})


@login_required
def td_create(request):
    """Créer un nouveau TD (pour contributeurs)."""
    if not request.user.is_contributor and not request.user.is_staff:
        messages.error(request, "Vous devez être contributeur pour créer un TD.")
        return redirect('td_list')
    
    if request.method == 'POST':
        form = TDCreateForm(request.POST, request.FILES)
        if form.is_valid():
            td = form.save(commit=False)
            td.author = request.user
            td.save()
            messages.success(request, "TD créé avec succès!")
            return redirect('td_detail', td_id=td.id)
    else:
        form = TDCreateForm()
    
    return render(request, 'learning/td_form.html', {'form': form, 'title': 'Créer un TD'})


@login_required
def td_update(request, td_id):
    """Modifier un TD existant (pour contributeurs)."""
    td = get_object_or_404(TD, id=td_id)
    
    if td.author != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission de modifier ce TD.")
        return redirect('td_detail', td_id=td.id)
    
    if request.method == 'POST':
        form = TDUpdateForm(request.POST, request.FILES, instance=td)
        if form.is_valid():
            form.save()
            messages.success(request, "TD modifié avec succès!")
            return redirect('td_detail', td_id=td.id)
    else:
        form = TDUpdateForm(instance=td)
    
    return render(request, 'learning/td_form.html', {'form': form, 'title': 'Modifier le TD', 'td': td})


@login_required
def corrected_td_create(request):
    """Créer une correction de TD (pour contributeurs)."""
    if not request.user.is_contributor and not request.user.is_staff:
        messages.error(request, "Vous devez être contributeur pour créer une correction.")
        return redirect('td_list')
    
    if request.method == 'POST':
        form = CorrectedTDCreateForm(request.POST, request.FILES)
        if form.is_valid():
            corrected_td = form.save(commit=False)
            corrected_td.author = request.user
            corrected_td.save()
            messages.success(request, "Correction créée avec succès!")
            return redirect('td_detail', td_id=corrected_td.td.id)
    else:
        form = CorrectedTDCreateForm()
    
    return render(request, 'learning/corrected_td_form.html', {'form': form, 'title': 'Créer une correction'})


@login_required
def corrected_td_update(request, corrected_td_id):
    """Modifier une correction de TD existante (pour contributeurs)."""
    corrected_td = get_object_or_404(CorrectedTD, id=corrected_td_id)
    
    if corrected_td.author != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas la permission de modifier cette correction.")
        return redirect('td_detail', td_id=corrected_td.td.id)
    
    if request.method == 'POST':
        form = CorrectedTDUpdateForm(request.POST, request.FILES, instance=corrected_td)
        if form.is_valid():
            form.save()
            messages.success(request, "Correction modifiée avec succès!")
            return redirect('td_detail', td_id=corrected_td.td.id)
    else:
        form = CorrectedTDUpdateForm(instance=corrected_td)
    
    return render(request, 'learning/corrected_td_form.html', {'form': form, 'title': 'Modifier la correction', 'corrected_td': corrected_td})
