from django.db import transaction
from django.utils import timezone
from .models import Exam, ExamSession, UserAnswer, Question, Choice


class ExamCorrectionService:
    """
    Service for strict QCM exam correction.
    Enforces exact match scoring: selected_answers must equal correct_answers.
    """
    
    @staticmethod
    def validate_question_integrity(question: Question) -> bool:
        """
        Validate that a question has at least one correct choice.
        Raises ValueError if validation fails.
        """
        correct_choices = question.choices.filter(is_correct=True).count()
        if correct_choices == 0:
            raise ValueError(f"Question {question.id} must have at least one correct choice.")
        return True
    
    @staticmethod
    def evaluate_answer(question: Question, selected_choice_ids: list) -> bool:
        """
        Evaluate a user's answer using strict QCM rules.
        
        Args:
            question: The Question being answered
            selected_choice_ids: List of choice IDs selected by the user
        
        Returns:
            bool: True if answer is correct (exact match), False otherwise
        """
        # Get correct choice IDs
        correct_choice_ids = set(
            question.choices.filter(is_correct=True).values_list('id', flat=True)
        )
        
        # Convert selected IDs to set for comparison
        selected_choice_ids_set = set(selected_choice_ids)
        
        # Strict evaluation: exact match required
        return selected_choice_ids_set == correct_choice_ids
    
    @staticmethod
    @transaction.atomic
    def submit_exam(session: ExamSession, answers_data: dict) -> dict:
        """
        Submit and grade an exam session.
        
        Args:
            session: The ExamSession to grade
            answers_data: Dict mapping question_id -> list of selected choice_ids
        
        Returns:
            dict: Correction results with score, XP, and per-question breakdown
        """
        exam = session.exam
        total_questions = exam.questions.count()
        correct_count = 0
        wrong_count = 0
        total_xp_earned = 0
        total_xp_penalty = 0
        question_results = []
        
        # Process each answer
        for question in exam.questions.all():
            # Validate question integrity
            ExamCorrectionService.validate_question_integrity(question)
            
            # Get user's selected choices for this question
            selected_choice_ids = answers_data.get(str(question.id), [])
            
            # Evaluate answer
            is_correct = ExamCorrectionService.evaluate_answer(question, selected_choice_ids)
            
            if is_correct:
                correct_count += 1
                total_xp_earned += exam.xp_per_correct
            else:
                wrong_count += 1
                total_xp_penalty += exam.xp_penalty_per_wrong
            
            # Create or update UserAnswer record
            user_answer, created = UserAnswer.objects.get_or_create(
                session=session,
                question=question,
                defaults={'is_correct': is_correct}
            )
            
            if not created:
                user_answer.is_correct = is_correct
                user_answer.save()
            
            # Store selected choices
            user_answer.selected_choices.set(selected_choice_ids)
            
            # Store result for response
            question_results.append({
                'question_id': question.id,
                'question_text': question.text,
                'is_correct': is_correct,
                'xp_earned': exam.xp_per_correct if is_correct else 0,
                'xp_penalty': exam.xp_penalty_per_wrong if not is_correct else 0,
                'correct_choice_ids': list(question.choices.filter(is_correct=True).values_list('id', flat=True)),
                'selected_choice_ids': selected_choice_ids,
            })
        
        # Calculate score (percentage)
        score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
        
        # Calculate net XP
        net_xp = total_xp_earned - total_xp_penalty
        
        # Update session
        session.score = score
        session.passed = score >= exam.passing_score
        session.is_completed = True
        session.completed_at = timezone.now()
        session.save()
        
        return {
            'session_id': session.id,
            'score': score,
            'passed': session.passed,
            'correct_count': correct_count,
            'wrong_count': wrong_count,
            'total_questions': total_questions,
            'total_xp_earned': total_xp_earned,
            'total_xp_penalty': total_xp_penalty,
            'net_xp': net_xp,
            'question_results': question_results,
        }
