from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Exam, ExamSession, Question
from .services import ExamCorrectionService
from gamification.services import XPService
from skills.services import SkillService
from recommendations.services import RecommendationService


@login_required
def exam_list(request):
    """List all available exams."""
    exams = Exam.objects.filter(is_active=True).select_related('subject')
    return render(request, 'exams/exam_list.html', {'exams': exams})


@login_required
def exam_detail(request, exam_id):
    """Show exam details before starting."""
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    return render(request, 'exams/exam_detail.html', {'exam': exam})


@login_required
def exam_take(request, exam_id):
    """
    Take an exam - display questions in QCM format or file-based format.
    Creates or retrieves an active session.
    """
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    user = request.user
    
    # Check if user has an incomplete session
    session, created = ExamSession.objects.get_or_create(
        user=user,
        exam=exam,
        defaults={'is_completed': False}
    )
    
    # If session is already completed, redirect to results
    if session.is_completed:
        return redirect('exam_result', session_id=session.id)
    
    # Get all questions with choices
    questions = exam.questions.all().prefetch_related('choices')
    
    return render(request, 'exams/exam_take.html', {
        'exam': exam,
        'session': session,
        'questions': questions,
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
    
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    user = request.user
    
    # Get or create session
    session, created = ExamSession.objects.get_or_create(
        user=user,
        exam=exam,
        defaults={'is_completed': False}
    )
    
    if session.is_completed:
        return redirect('exam_result', session_id=session.id)
    
    # Extract answers from POST data
    answers_data = {}
    for key, value in request.POST.items():
        if key.startswith('question_'):
            question_id = key.replace('question_', '')
            if isinstance(value, list):
                answers_data[question_id] = value
            else:
                answers_data[question_id] = [value]
    
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
    
    # Update XP (high XP for exam completion)
    xp_service = XPService()
    xp_earned = xp_service.award_xp(
        user=user,
        amount=100 if results['passed'] else 50,
        reason=f"Examen terminé : {exam.title}",
        action_type='exam'
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
    """Display exam results with detailed breakdown."""
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    
    if not session.is_completed:
        return redirect('exam_take', exam_id=session.exam.id)
    
    answers = session.answers.select_related('question').prefetch_related('selected_choices')
    
    return render(request, 'exams/exam_result.html', {
        'session': session,
        'answers': answers,
    })
