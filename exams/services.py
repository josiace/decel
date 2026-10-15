from django.db import transaction
from django.utils import timezone
from .models import ExamSession, UserAnswer, Question


class ExamCorrectionService:
    """Correction stricte des QCM : les choix doivent correspondre exactement."""

    @staticmethod
    def validate_question_integrity(question: Question) -> bool:
        if not question.choices.filter(is_correct=True).exists():
            raise ValueError(f"Question {question.id} must have at least one correct choice.")
        return True

    @staticmethod
    def evaluate_answer(question: Question, selected_choice_ids: list) -> bool:
        correct_ids = set(question.choices.filter(is_correct=True).values_list("id", flat=True))
        try:
            selected_ids = {int(choice_id) for choice_id in selected_choice_ids}
        except (TypeError, ValueError):
            raise ValueError("Identifiant de réponse invalide.") from None
        valid_ids = set(question.choices.values_list("id", flat=True))
        if not selected_ids.issubset(valid_ids):
            raise ValueError(f"Un choix ne correspond pas à la question {question.id}.")
        return selected_ids == correct_ids

    @staticmethod
    @transaction.atomic
    def submit_exam(session: ExamSession, answers_data: dict) -> dict:
        # Verrouille la tentative pour empêcher deux soumissions concurrentes.
        session = ExamSession.objects.select_for_update().select_related("exam").get(pk=session.pk)
        if session.is_completed:
            raise ValueError("Cette tentative a déjà été soumise.")

        exam = session.exam
        questions = list(exam.questions.prefetch_related("choices").all())
        question_ids = {str(question.id) for question in questions}
        if set(answers_data) - question_ids:
            raise ValueError("Des réponses concernent des questions étrangères à cet examen.")

        total_questions = len(questions)
        correct_count = wrong_count = total_xp_earned = total_xp_penalty = 0
        question_results = []

        for question in questions:
            ExamCorrectionService.validate_question_integrity(question)
            try:
                selected_ids = [int(value) for value in answers_data.get(str(question.id), [])]
            except (TypeError, ValueError):
                raise ValueError("Identifiant de réponse invalide.") from None

            is_correct = ExamCorrectionService.evaluate_answer(question, selected_ids)
            if is_correct:
                correct_count += 1
                total_xp_earned += exam.xp_per_correct
            else:
                wrong_count += 1
                total_xp_penalty += exam.xp_penalty_per_wrong

            answer, created = UserAnswer.objects.get_or_create(
                session=session, question=question, defaults={"is_correct": is_correct}
            )
            if not created:
                answer.is_correct = is_correct
                answer.save(update_fields=["is_correct"])
            answer.selected_choices.set(selected_ids)

            question_results.append({
                "question_id": question.id,
                "question_text": question.text,
                "is_correct": is_correct,
                "xp_earned": exam.xp_per_correct if is_correct else 0,
                "xp_penalty": exam.xp_penalty_per_wrong if not is_correct else 0,
                "correct_choice_ids": list(question.choices.filter(is_correct=True).values_list("id", flat=True)),
                "selected_choice_ids": selected_ids,
            })

        score = int(correct_count * 100 / total_questions) if total_questions else 0
        net_xp = total_xp_earned - total_xp_penalty
        session.score = score
        session.passed = score >= exam.passing_score
        session.is_completed = True
        session.completed_at = timezone.now()
        session.save(update_fields=["score", "passed", "is_completed", "completed_at"])

        return {
            "session_id": session.id,
            "score": score,
            "passed": session.passed,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "total_questions": total_questions,
            "total_xp_earned": total_xp_earned,
            "total_xp_penalty": total_xp_penalty,
            "net_xp": net_xp,
            "question_results": question_results,
        }
