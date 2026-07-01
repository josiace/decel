from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import FileResponse, Http404
from django.db import transaction
from .models import Content, ModerationRule
from skills.models import Subject
from gamification.services import XPService


def is_staff_user(user):
    """Check if user is staff."""
    return user.is_staff


def content_list(request):
    """List approved community content - public pour SEO."""
    contents = Content.objects.filter(status='approved').select_related('subject', 'author')
    return render(request, 'community/content_list.html', {'contents': contents})


@login_required
def my_content(request):
    """List content submitted by the current user."""
    contents = Content.objects.filter(author=request.user).select_related('subject')
    return render(request, 'community/my_content.html', {'contents': contents})


@login_required
def content_create(request):
    """Create new community content."""
    subjects = Subject.objects.all()
    
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        content_format = request.POST.get('content_format')
        content = request.POST.get('content', '')
        content_file = request.FILES.get('content_file')
        dc_price = request.POST.get('dc_price', 0)
        subject_id = request.POST.get('subject')
        
        if not all([content_type, title, subject_id]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return render(request, 'community/content_form.html', {
                'subjects': subjects,
            })
        
        # Validate content based on format
        if content_format == 'text' and not content:
            messages.error(request, 'Le contenu texte est requis pour le format texte.')
            return render(request, 'community/content_form.html', {'subjects': subjects})
        
        if content_format in ['pdf', 'file'] and not content_file:
            messages.error(request, 'Le fichier est requis pour ce format.')
            return render(request, 'community/content_form.html', {'subjects': subjects})
        
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Create content as draft
        new_content = Content.objects.create(
            title=title,
            description=description,
            content_type=content_type,
            content_format=content_format,
            content=content,
            content_file=content_file,
            dc_price=int(dc_price),
            subject=subject,
            author=request.user,
            status='draft'
        )
        
        messages.success(request, 'Contenu créé avec succès. Soumettez-le pour modération lorsqu\'il est prêt.')
        return redirect('my_content')
    
    return render(request, 'community/content_form.html', {'subjects': subjects})


@login_required
def content_edit(request, content_id):
    """Edit existing community content."""
    content = get_object_or_404(Content, id=content_id)
    
    if not content.can_edit(request.user):
        messages.error(request, 'Vous n\'avez pas la permission de modifier ce contenu.')
        return redirect('my_content')
    
    subjects = Subject.objects.all()
    
    if request.method == 'POST':
        content.title = request.POST.get('title')
        content.description = request.POST.get('description', '')
        content.content_format = request.POST.get('content_format')
        content.content = request.POST.get('content', '')
        content_file = request.FILES.get('content_file')
        content.dc_price = int(request.POST.get('dc_price', 0))
        content.subject_id = request.POST.get('subject')
        
        # Validate content based on format
        if content.content_format == 'text' and not content.content:
            messages.error(request, 'Le contenu texte est requis pour le format texte.')
            return render(request, 'community/content_form.html', {
                'content': content,
                'subjects': subjects,
            })
        
        if content.content_format in ['pdf', 'file'] and not content.content_file and not content.content_file:
            messages.error(request, 'Le fichier est requis pour ce format.')
            return render(request, 'community/content_form.html', {
                'content': content,
                'subjects': subjects,
            })
        
        # Update file if provided
        if content_file:
            content.content_file = content_file
        
        content.save()
        
        messages.success(request, 'Contenu mis à jour avec succès.')
        return redirect('my_content')
    
    return render(request, 'community/content_form.html', {
        'content': content,
        'subjects': subjects,
    })


@login_required
def content_submit(request, content_id):
    """Submit content for moderation."""
    content = get_object_or_404(Content, id=content_id, author=request.user)
    
    if content.status != 'draft':
        messages.error(request, 'Seul le contenu en brouillon peut être soumis.')
        return redirect('my_content')
    
    content.status = 'pending'
    content.save()
    
    messages.success(request, 'Contenu soumis pour modération.')
    return redirect('my_content')


@user_passes_test(is_staff_user)
@login_required
def moderation_queue(request):
    """Show pending content for moderation."""
    pending_contents = Content.objects.filter(status='pending').select_related('subject', 'author')
    return render(request, 'community/moderation_queue.html', {'contents': pending_contents})


@user_passes_test(is_staff_user)
@login_required
def moderate_content(request, content_id):
    """Approve or reject content."""
    content = get_object_or_404(Content, id=content_id)
    
    if not content.can_moderate(request.user):
        messages.error(request, 'Vous n\'avez pas la permission de modérer ce contenu.')
        return redirect('moderation_queue')
    
    if request.method == 'POST':
        action = request.POST.get('action')  # 'approve' or 'reject'
        notes = request.POST.get('moderation_notes', '')
        rule_id = request.POST.get('moderation_rule')
        
        if action not in ['approve', 'reject']:
            messages.error(request, 'Action invalide.')
            return redirect('moderation_queue')
        
        content.status = 'approved' if action == 'approve' else 'rejected'
        content.moderation_notes = notes
        content.moderated_by = request.user
        content.moderated_at = timezone.now()
        
        if rule_id:
            content.moderation_rule_id = rule_id
        
        content.save()
        
        messages.success(request, f'Contenu {action}é avec succès.')
        return redirect('moderation_queue')
    
    rules = ModerationRule.objects.filter(is_active=True)
    return render(request, 'community/moderate_content.html', {
        'content': content,
        'rules': rules,
    })


@login_required
def content_detail(request, content_id):
    """Show community content details."""
    content = get_object_or_404(Content, id=content_id, status='approved')

    # Check if user can access the content (free or author)
    can_access = content.dc_price == 0 or content.author == request.user

    # Check if user has purchased the content
    from .models import ContentPurchase
    has_purchased = ContentPurchase.objects.filter(user=request.user, content=content).exists()

    # User can access if free, author, or has purchased
    can_access = can_access or has_purchased

    return render(request, 'community/content_detail.html', {
        'content': content,
        'can_access': can_access,
        'has_purchased': has_purchased,
    })


@login_required
def purchase_content(request, content_id):
    """Purchase community content with DC."""
    from accounts.services import DCService
    from .models import ContentPurchase

    content = get_object_or_404(Content, id=content_id, status='approved')

    if content.dc_price == 0:
        messages.success(request, 'Ce contenu est gratuit.')
        return redirect('content_detail', content_id=content.id)

    if content.author == request.user:
        messages.success(request, 'Vous êtes l\'auteur de ce contenu.')
        return redirect('content_detail', content_id=content.id)

    # Check if user has already purchased this content
    if ContentPurchase.objects.filter(user=request.user, content=content).exists():
        messages.info(request, 'Vous avez déjà acheté ce contenu.')
        return redirect('content_detail', content_id=content.id)

    # Traiter l'achat avec DCService (débiter acheteur, créditer créateur)
    success, message = DCService.process_content_purchase(
        purchaser=request.user,
        content_type='community_content',
        content_id=content.id,
        price=content.dc_price,
        author=content.author
    )

    if not success:
        messages.error(request, message)
        return redirect('content_detail', content_id=content.id)

    # Create purchase record
    ContentPurchase.objects.create(
        user=request.user,
        content=content,
        price_paid=content.dc_price
    )

    messages.success(request, f'Contenu acheté avec succès pour {content.dc_price} DC.')
    return redirect('content_detail', content_id=content.id)


@login_required
def download_file(request, content_id):
    """Download community content file."""
    content = get_object_or_404(Content, id=content_id, status='approved')

    # Check if user can access (free, author, or has purchased)
    from .models import ContentPurchase
    has_purchased = ContentPurchase.objects.filter(user=request.user, content=content).exists()
    can_access = content.dc_price == 0 or content.author == request.user or has_purchased

    if not can_access:
        messages.error(request, "Vous devez acheter ce contenu pour le télécharger.")
        return redirect('content_detail', content_id=content.id)

    if not content.content_file:
        raise Http404("Aucun fichier disponible")

    try:
        response = FileResponse(content.content_file.open('rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{content.content_file.name.split("/")[-1]}"'
        return response
    except Exception as e:
        messages.error(request, f"Erreur lors du téléchargement : {str(e)}")
        return redirect(request.META.get('HTTP_REFERER', '/'))
