from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from accounts.models import User, Contributor
from learning.models import Course, TD, CorrectedTD
from exams.models import Exam, Question, Choice
from community.models import Content
from .forms import ExamCreateForm, QuestionCreateForm, ChoiceForm


@login_required
def contributor_dashboard(request):
    """Dashboard personnel pour les contributeurs."""
    # Check if user is a contributor
    if not request.user.is_contributor():
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')

    contributor = request.user.contributor

    # Get statistics
    stats = {
        'courses_count': 0,
        'exams_count': 0,
        'community_content_count': 0,
    }

    if contributor.can_create_courses:
        stats['courses_count'] = Course.objects.filter(author=request.user).count()

    if contributor.can_create_exams:
        stats['exams_count'] = Exam.objects.filter(created_by=request.user).count()

    if contributor.can_create_community_content:
        stats['community_content_count'] = Content.objects.filter(author=request.user).count()

    # Get recent content
    recent_content = []

    if contributor.can_create_courses:
        recent_courses = Course.objects.filter(author=request.user).order_by('-created_at')[:3]
        for course in recent_courses:
            recent_content.append({
                'type': 'Cours',
                'title': course.title,
                'subject': course.subject.name if course.subject else 'N/A',
                'created_at': course.created_at,
                'url': f'/learning/courses/{course.id}/'
            })

    if contributor.can_create_exams:
        recent_exams = Exam.objects.filter(created_by=request.user).order_by('-created_at')[:3]
        for exam in recent_exams:
            recent_content.append({
                'type': 'Examen',
                'title': exam.title,
                'subject': exam.subject.name if exam.subject else 'N/A',
                'created_at': exam.created_at,
                'url': f'/exams/{exam.id}/'
            })

    if contributor.can_create_community_content:
        recent_community = Content.objects.filter(author=request.user).order_by('-created_at')[:3]
        for content in recent_community:
            recent_content.append({
                'type': 'Contenu Communautaire',
                'title': content.title,
                'subject': content.subject.name if content.subject else 'N/A',
                'created_at': content.created_at,
                'url': f'/community/content/{content.id}/'
            })

    # Sort by creation date
    recent_content.sort(key=lambda x: x['created_at'], reverse=True)
    recent_content = recent_content[:5]

    return render(request, 'contributor/dashboard.html', {
        'contributor': contributor,
        'stats': stats,
        'recent_content': recent_content,
    })


@login_required
def pro_upgrade(request):
    """Page de présentation des plans Créateur Pro et Académie."""
    if not request.user.is_contributor():
        messages.error(request, "Vous devez être contributeur pour accéder à cette page.")
        return redirect('dashboard')

    contributor = request.user.contributor
    return render(request, 'contributor/pro_upgrade.html', {
        'contributor': contributor,
        'is_pro': contributor.is_pro,
    })


@login_required
def creator_analytics(request):
    """
    Tableau de bord analytique du créateur.
    Statistiques basiques accessibles à tous les contributeurs.
    Détails avancés réservés aux abonnements Pro/Académie.
    """
    if not request.user.is_contributor():
        messages.error(request, "Accès réservé aux contributeurs.")
        return redirect('dashboard')

    contributor = request.user.contributor
    is_pro = contributor.is_pro

    from accounts.models import DCTransaction
    from community.models import ContentPurchase as CommunityPurchase

    # DC gagnés via ventes
    sales_qs = DCTransaction.objects.filter(
        user=request.user, transaction_type='sale'
    )
    total_dc_from_sales = sales_qs.aggregate(total=Sum('amount'))['total'] or 0
    recent_sales = sales_qs.order_by('-created_at')[:10] if is_pro else sales_qs.order_by('-created_at')[:3]

    # Contenu publié
    courses = Course.objects.filter(author=request.user).select_related('subject')
    exams = Exam.objects.filter(created_by=request.user).select_related('subject')
    community_content = Content.objects.filter(
        author=request.user, status='approved'
    ).select_related('subject')

    # Achats de contenu communautaire (visible Pro uniquement)
    community_purchases = []
    total_community_purchases = 0
    if is_pro:
        community_purchases = CommunityPurchase.objects.filter(
            content__author=request.user
        ).select_related('content', 'user').order_by('-purchased_at')[:20]
        total_community_purchases = CommunityPurchase.objects.filter(
            content__author=request.user
        ).count()

    context = {
        'contributor': contributor,
        'is_pro': is_pro,
        'total_dc_from_sales': total_dc_from_sales,
        'recent_sales': recent_sales,
        'courses': courses,
        'exams': exams,
        'community_content': community_content,
        'courses_count': courses.count(),
        'exams_count': exams.count(),
        'community_content_count': community_content.count(),
        'community_purchases': community_purchases,
        'total_community_purchases': total_community_purchases,
    }
    return render(request, 'contributor/analytics.html', context)


@login_required
def contributor_courses(request):
    """Liste des cours créés par le contributeur."""
    if not request.user.is_contributor() or not request.user.contributor.can_create_courses:
        messages.error(request, "Vous n'avez pas la permission de créer des cours.")
        return redirect('contributor_dashboard')

    courses = Course.objects.filter(author=request.user).select_related('subject')

    return render(request, 'contributor/courses.html', {
        'courses': courses,
    })


@login_required
def contributor_exams(request):
    """Liste des examens créés par le contributeur."""
    if not request.user.is_contributor() or not request.user.contributor.can_create_exams:
        messages.error(request, "Vous n'avez pas la permission de créer des examens.")
        return redirect('contributor_dashboard')

    exams = Exam.objects.filter(created_by=request.user).select_related('subject')

    return render(request, 'contributor/exams.html', {
        'exams': exams,
    })


@login_required
def contributor_community(request):
    """Liste du contenu communautaire créé par le contributeur."""
    if not request.user.is_contributor() or not request.user.contributor.can_create_community_content:
        messages.error(request, "Vous n'avez pas la permission de créer du contenu communautaire.")
        return redirect('contributor_dashboard')

    content = Content.objects.filter(author=request.user).select_related('subject')

    return render(request, 'contributor/community.html', {
        'content': content,
    })


@login_required
def create_exam(request):
    """Créer un nouvel examen avec interface intuitive."""
    if not request.user.is_contributor() or not request.user.contributor.can_create_exams:
        messages.error(request, "Vous n'avez pas la permission de créer des examens.")
        return redirect('contributor_dashboard')

    if request.method == 'POST':
        form = ExamCreateForm(request.POST, request.FILES)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, f"Examen '{exam.title}' créé avec succès !")
            return redirect('contributor:add_questions', exam_id=exam.id)
    else:
        form = ExamCreateForm()

    return render(request, 'contributor/create_exam.html', {
        'form': form,
    })


@login_required
def add_questions(request, exam_id):
    """Ajouter des questions à un examen avec interface intuitive."""
    if not request.user.is_contributor() or not request.user.contributor.can_create_exams:
        messages.error(request, "Vous n'avez pas la permission de créer des examens.")
        return redirect('contributor_dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)

    if request.method == 'POST':
        # Get the next question order
        next_order = exam.questions.count() + 1

        # Create the question
        question = Question.objects.create(
            exam=exam,
            order=next_order,
            text=''  # Empty for file-based exams
        )

        # Create choices from POST data
        choice_count = 0
        for key in request.POST:
            if key.startswith('option_label_'):
                index = key.split('_')[-1]
                label = request.POST.get(f'option_label_{index}')
                text = request.POST.get(f'option_text_{index}')
                is_correct = request.POST.get(f'option_correct_{index}') == 'on'

                if text:
                    Choice.objects.create(
                        question=question,
                        label=label if label else None,
                        text=text,
                        is_correct=is_correct,
                        order=choice_count
                    )
                    choice_count += 1

        if choice_count > 0:
            # Check if at least one choice is correct
            correct_count = question.choices.filter(is_correct=True).count()
            if correct_count == 0:
                messages.warning(request, "Attention : Aucune réponse correcte cochée pour cette question.")
            else:
                messages.success(request, f"Question {next_order} ajoutée avec {choice_count} choix !")
        else:
            question.delete()
            messages.error(request, "Veuillez ajouter au moins une option de réponse.")

        return redirect('contributor:add_questions', exam_id=exam.id)

    questions = exam.questions.all().prefetch_related('choices').order_by('order')

    return render(request, 'contributor/add_questions.html', {
        'exam': exam,
        'questions': questions,
    })


@login_required
def delete_question(request, exam_id, question_id):
    """Supprimer une question."""
    if not request.user.is_contributor() or not request.user.contributor.can_create_exams:
        messages.error(request, "Vous n'avez pas la permission de créer des examens.")
        return redirect('contributor_dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    question = get_object_or_404(Question, id=question_id, exam=exam)

    if request.method == 'POST':
        question.delete()
        messages.success(request, "Question supprimée avec succès.")
        return redirect('contributor:add_questions', exam_id=exam.id)

    return render(request, 'contributor/delete_question.html', {
        'exam': exam,
        'question': question,
    })


@login_required
def edit_exam(request, exam_id):
    """Modifier un examen existant."""
    if not request.user.is_contributor() or not request.user.contributor.can_create_exams:
        messages.error(request, "Vous n'avez pas la permission de modifier des examens.")
        return redirect('contributor_dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)

    if request.method == 'POST':
        form = ExamCreateForm(request.POST, request.FILES, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f"Examen '{exam.title}' modifié avec succès !")
            return redirect('contributor:exams')
    else:
        form = ExamCreateForm(instance=exam)

    return render(request, 'contributor/edit_exam.html', {
        'form': form,
        'exam': exam,
    })
