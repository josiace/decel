from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import random
from .models import Exam, ExamSession, Question
from .services import ExamCorrectionService
from gamification.services import XPService
from skills.services import SkillService
from recommendations.services import RecommendationService


def exam_list(request):
    """List all available exams - public pour SEO."""
    exams = Exam.objects.filter(is_active=True).select_related('subject')
    context = {
        'exams': exams,
        'meta_description': 'Découvrez tous les examens QCM disponibles sur DECEL. Testez vos connaissances en Mathématiques, Physique, Chimie et plus. Gagnez des XP et améliorez vos compétences.',
    }
    return render(request, 'exams/exam_list.html', context)


def exam_detail(request, exam_id):
    """Show exam details before starting - public pour SEO."""
    exam = get_object_or_404(Exam.objects.select_related('subject', 'created_by'), id=exam_id, is_active=True)
    context = {
        'exam': exam,
        'meta_description': f"Examen QCM : {exam.title} en {exam.subject.name}. Niveau de difficulté {exam.difficulty}/5. Testez vos connaissances et gagnez des XP. Score de passage : {exam.passing_score}%.",
    }
    return render(request, 'exams/exam_detail.html', context)


@login_required
def exam_take(request, exam_id):
    """
    Take an exam - display questions in QCM format or file-based format.
    Creates a new session each time (allows multiple attempts).
    Prevents exam creators from taking their own exams (anti-XP farming).
    """
    exam = get_object_or_404(Exam.objects.select_related('subject', 'created_by'), id=exam_id, is_active=True)
    user = request.user

    # Prevent exam creators from taking their own exams
    if exam.created_by == user:
        from django.contrib import messages
        messages.error(request, "Vous ne pouvez pas passer vos propres examens.")
        return redirect('exam_detail', exam_id=exam_id)

    # Create a new session (allows multiple attempts)
    session = ExamSession.objects.create(
        user=user,
        exam=exam,
        is_completed=False
    )

    # Initialize timer for sessions with time limit
    if exam.time_limit:
        from django.utils import timezone
        session.time_remaining_seconds = exam.time_limit * 60  # Convert minutes to seconds
        session.save()

    # Get all questions with choices
    questions = exam.questions.all().prefetch_related('choices')
    
    # Randomize questions if enabled
    if exam.randomize_questions:
        questions = list(questions)
        random.shuffle(questions)
    
    # Randomize choices if enabled
    if exam.randomize_choices:
        for question in questions:
            choices = list(question.choices.all())
            random.shuffle(choices)
            question.choices.all = lambda: choices  # Override the queryset

    return render(request, 'exams/exam_take.html', {
        'exam': exam,
        'session': session,
        'questions': questions,
        'time_limit_minutes': exam.time_limit,
        'time_remaining_seconds': session.time_remaining_seconds,
    })


@login_required
def exam_submit(request, exam_id):
    """
    Submit exam answers for correction.
    Uses ExamCorrectionService for strict QCM grading.
    Triggers XP, skill, and recommendation updates.
    """
    if request.method != 'POST':
        return redirect('exam_take', exam_id=exam_id)

    exam = get_object_or_404(Exam.objects.select_related('subject', 'created_by'), id=exam_id, is_active=True)
    user = request.user

    # Get the active session (created in exam_take)
    session = get_object_or_404(ExamSession, user=user, exam=exam, is_completed=False)

    if session.is_completed:
        return redirect('exam_result', session_id=session.id)
    
    # Extract answers from POST data
    answers_data = {}
    for key, value in request.POST.items():
        if key.startswith('question_'):
            question_id = key.replace('question_', '')
            if isinstance(value, list):
                # Convert all choice IDs to integers
                answers_data[question_id] = [int(v) for v in value]
            else:
                answers_data[question_id] = [int(value)]
    
    # Validate that all questions have answers
    unanswered_questions = []
    for question in exam.questions.all():
        if str(question.id) not in answers_data or not answers_data[str(question.id)]:
            unanswered_questions.append(question.id)
    
    if unanswered_questions:
        return render(request, 'exams/exam_take.html', {
            'exam': exam,
            'session': session,
            'questions': exam.questions.all().prefetch_related('choices'),
            'error': 'Veuillez répondre à toutes les questions avant de soumettre.',
        })
    
    # Submit and grade exam
    correction_service = ExamCorrectionService()
    results = correction_service.submit_exam(session, answers_data)

    # Check if this is the best attempt for this exam
    previous_sessions = ExamSession.objects.filter(user=user, exam=exam, is_completed=True)
    best_previous_score = previous_sessions.exclude(id=session.id).order_by('-score').first()
    should_award_xp = False

    if best_previous_score is None:
        # First attempt - always award XP
        should_award_xp = True
        session.is_best_attempt = True
    elif results['score'] > best_previous_score.score:
        # Better score than previous best - award XP and mark as best
        should_award_xp = True
        session.is_best_attempt = True
        # Unmark previous best attempt
        best_previous_score.is_best_attempt = False
        best_previous_score.save()
    elif results['passed'] and not best_previous_score.passed:
        # First time passing - award XP
        should_award_xp = True
        session.is_best_attempt = True

    session.save()

    # Update XP (per-question system) - only if this is the best attempt
    xp_service = XPService()
    if should_award_xp and results['net_xp'] > 0:
        xp_earned = xp_service.award_xp(
            user=user,
            amount=results['net_xp'],
            reason=f"Examen terminé : {exam.title} (+{results['total_xp_earned']} XP, -{results['total_xp_penalty']} XP) - Meilleure tentative",
            action_type='exam'
        )
        session.xp_earned = results['net_xp']
        session.save()
    elif should_award_xp and results['net_xp'] < 0:
        # Handle negative XP (penalty) only for best attempt
        xp_service.award_xp(
            user=user,
            amount=results['net_xp'],
            reason=f"Examen terminé : {exam.title} (+{results['total_xp_earned']} XP, -{results['total_xp_penalty']} XP) - Meilleure tentative",
            action_type='exam'
        )
        session.xp_earned = results['net_xp']
        session.save()

    # Award DC for passing exams (score >= 50%)
    from accounts.services import DCService
    if results['passed']:
        dc_transaction = DCService.award_exam_reward(user, exam.id, results['score'])
        if dc_transaction:
            session.dc_earned = dc_transaction.amount
            session.save()
        session.save()

        # Award XP to contributor if exam was created by a contributor and user failed
        if exam.created_by and exam.created_by.is_contributor() and not results['passed']:
            contributor_reward = exam.xp_reward_for_contributor
            if contributor_reward > 0:
                xp_service.award_xp(
                    user=exam.created_by,
                    amount=contributor_reward,
                    reason=f"Récompense contributeur : Un utilisateur a raté votre examen '{exam.title}'",
                    action_type='contributor_reward'
                )
    
    # Update skill for the subject
    skill_service = SkillService()
    skill_service.update_skill_from_exam(
        user=user,
        subject=exam.subject,
        score=results['score'],
        passed=results['passed']
    )
    
    # Generate recommendations based on performance
    recommendation_service = RecommendationService()
    if results['passed']:
        recommendation_service.generate_recommendation(
            user=user,
            recommendation_type='advance',
            context={'subject': exam.subject.name, 'exam_score': results['score']}
        )
    else:
        recommendation_service.generate_recommendation(
            user=user,
            recommendation_type='review',
            context={'subject': exam.subject.name, 'exam_score': results['score']}
        )
    
    return redirect('exam_result', session_id=session.id)


@login_required
def exam_result(request, session_id):
    """Display exam results with detailed breakdown - optimisé."""
    session = get_object_or_404(
        ExamSession.objects.select_related('exam', 'exam__subject', 'user'),
        id=session_id,
        user=request.user
    )

    if not session.is_completed:
        return redirect('exam_take', exam_id=session.exam.id)

    answers = session.answers.select_related('question').prefetch_related('selected_choices')

    return render(request, 'exams/exam_result.html', {
        'session': session,
        'answers': answers,
    })


@login_required
def exam_time_expired(request, exam_id):
    """
    Handle automatic submission when timer expires.
    Called via AJAX when time runs out.
    """
    if request.method != 'POST':
        return redirect('exam_take', exam_id=exam_id)
    
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    user = request.user
    
    # Get session
    session = get_object_or_404(ExamSession, user=user, exam=exam, is_completed=False)
    
    # Mark as time expired
    session.is_time_expired = True
    
    # Get current answers (partial submission)
    answers_data = {}
    for key, value in request.POST.items():
        if key.startswith('question_'):
            question_id = key.replace('question_', '')
            if isinstance(value, list):
                # Convert all choice IDs to integers
                answers_data[question_id] = [int(v) for v in value]
            else:
                answers_data[question_id] = [int(value)]
    
    # Submit with current answers
    correction_service = ExamCorrectionService()
    results = correction_service.submit_exam(session, answers_data)

    # Check if this is the best attempt for this exam
    previous_sessions = ExamSession.objects.filter(user=user, exam=exam, is_completed=True)
    best_previous_score = previous_sessions.exclude(id=session.id).order_by('-score').first()
    should_award_xp = False

    if best_previous_score is None:
        # First attempt - always award XP
        should_award_xp = True
        session.is_best_attempt = True
    elif results['score'] > best_previous_score.score:
        # Better score than previous best - award XP and mark as best
        should_award_xp = True
        session.is_best_attempt = True
        # Unmark previous best attempt
        best_previous_score.is_best_attempt = False
        best_previous_score.save()
    elif results['passed'] and not best_previous_score.passed:
        # First time passing - award XP
        should_award_xp = True
        session.is_best_attempt = True

    session.save()

    # Update XP - only if this is the best attempt
    xp_service = XPService()
    if should_award_xp and results['net_xp'] != 0:
        xp_service.award_xp(
            user=user,
            amount=results['net_xp'],
            reason=f"Examen expiré : {exam.title} (+{results['total_xp_earned']} XP, -{results['total_xp_penalty']} XP) - Meilleure tentative",
            action_type='exam'
        )
        session.xp_earned = results['net_xp']
        session.save()

        # Award XP to contributor if exam was created by a contributor and user failed
        if exam.created_by and exam.created_by.is_contributor() and not results['passed']:
            contributor_reward = exam.xp_reward_for_contributor
            if contributor_reward > 0:
                xp_service.award_xp(
                    user=exam.created_by,
                    amount=contributor_reward,
                    reason=f"Récompense contributeur : Un utilisateur a raté votre examen '{exam.title}' (temps expiré)",
                    action_type='contributor_reward'
                )
    
    # Update skill
    skill_service = SkillService()
    skill_service.update_skill_from_exam(
        user=user,
        subject=exam.subject,
        score=results['score'],
        passed=results['passed']
    )
    
    return redirect('exam_result', session_id=session.id)
