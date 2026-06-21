"""
Tests pour ExamCorrectionService — moteur de correction QCM strict.
Couvre : evaluate_answer, validate_question_integrity, submit_exam.
"""
from django.test import TestCase
from accounts.models import User
from skills.models import Subject
from exams.models import Exam, Question, Choice, ExamSession
from exams.services import ExamCorrectionService


def make_user(email='examuser@test.com'):
    return User.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='testpass123',
        first_name='Exam',
        last_name='User',
    )


def make_exam_with_question(user, correct_labels=('A',), wrong_labels=('B', 'C')):
    """
    Crée un examen avec une question et des choix.
    correct_labels : labels des bonnes réponses.
    wrong_labels   : labels des mauvaises réponses.
    Retourne (exam, question, correct_choices, wrong_choices).
    """
    subject = Subject.objects.create(name='Maths Test')
    exam = Exam.objects.create(
        title='Examen Test',
        subject=subject,
        passing_score=60,
        created_by=user,
    )
    question = Question.objects.create(exam=exam, order=1, text='2 + 2 = ?')

    correct_choices = []
    for label in correct_labels:
        c = Choice.objects.create(question=question, label=label, text=f'Option {label}', is_correct=True)
        correct_choices.append(c)

    wrong_choices = []
    for label in wrong_labels:
        c = Choice.objects.create(question=question, label=label, text=f'Option {label}', is_correct=False)
        wrong_choices.append(c)

    return exam, question, correct_choices, wrong_choices


class EvaluateAnswerTest(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_single_correct_answer_exact_match(self):
        _, question, correct, wrong = make_exam_with_question(self.user)
        result = ExamCorrectionService.evaluate_answer(question, [correct[0].id])
        self.assertTrue(result)

    def test_single_wrong_answer(self):
        _, question, correct, wrong = make_exam_with_question(self.user)
        result = ExamCorrectionService.evaluate_answer(question, [wrong[0].id])
        self.assertFalse(result)

    def test_no_answer_selected(self):
        _, question, correct, wrong = make_exam_with_question(self.user)
        result = ExamCorrectionService.evaluate_answer(question, [])
        self.assertFalse(result)

    def test_multiple_correct_exact_match(self):
        """Deux bonnes réponses requises, les deux sélectionnées → correct."""
        _, question, correct, wrong = make_exam_with_question(
            self.user, correct_labels=('A', 'B'), wrong_labels=('C',)
        )
        ids = [c.id for c in correct]
        result = ExamCorrectionService.evaluate_answer(question, ids)
        self.assertTrue(result)

    def test_partial_answer_fails_strict(self):
        """Deux bonnes réponses requises, une seule sélectionnée → incorrect (strict)."""
        _, question, correct, wrong = make_exam_with_question(
            self.user, correct_labels=('A', 'B'), wrong_labels=('C',)
        )
        result = ExamCorrectionService.evaluate_answer(question, [correct[0].id])
        self.assertFalse(result)

    def test_correct_plus_extra_wrong_fails(self):
        """Bonne réponse + mauvaise réponse en plus → incorrect."""
        _, question, correct, wrong = make_exam_with_question(self.user)
        result = ExamCorrectionService.evaluate_answer(
            question, [correct[0].id, wrong[0].id]
        )
        self.assertFalse(result)

    def test_all_wrong_answers(self):
        _, question, correct, wrong = make_exam_with_question(
            self.user, correct_labels=('A',), wrong_labels=('B', 'C')
        )
        result = ExamCorrectionService.evaluate_answer(
            question, [wrong[0].id, wrong[1].id]
        )
        self.assertFalse(result)


class ValidateQuestionIntegrityTest(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_valid_question_passes(self):
        _, question, correct, wrong = make_exam_with_question(self.user)
        result = ExamCorrectionService.validate_question_integrity(question)
        self.assertTrue(result)

    def test_question_without_correct_choice_raises(self):
        subject = Subject.objects.create(name='Matière Sans Réponse')
        exam = Exam.objects.create(title='Exam Sans Réponse', subject=subject, created_by=self.user)
        question = Question.objects.create(exam=exam, order=1, text='Question invalide')
        Choice.objects.create(question=question, text='Mauvaise', is_correct=False)

        with self.assertRaises(ValueError):
            ExamCorrectionService.validate_question_integrity(question)


class SubmitExamTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.exam, self.question, self.correct, self.wrong = make_exam_with_question(
            self.user, correct_labels=('A',), wrong_labels=('B', 'C')
        )
        self.session = ExamSession.objects.create(user=self.user, exam=self.exam)

    def test_submit_with_correct_answer(self):
        answers = {str(self.question.id): [self.correct[0].id]}
        result = ExamCorrectionService.submit_exam(self.session, answers)
        self.assertEqual(result['score'], 100)
        self.assertTrue(result['passed'])
        self.assertEqual(result['correct_count'], 1)
        self.assertEqual(result['wrong_count'], 0)

    def test_submit_with_wrong_answer(self):
        answers = {str(self.question.id): [self.wrong[0].id]}
        result = ExamCorrectionService.submit_exam(self.session, answers)
        self.assertEqual(result['score'], 0)
        self.assertFalse(result['passed'])
        self.assertEqual(result['correct_count'], 0)
        self.assertEqual(result['wrong_count'], 1)

    def test_submit_marks_session_completed(self):
        answers = {str(self.question.id): [self.correct[0].id]}
        ExamCorrectionService.submit_exam(self.session, answers)
        self.session.refresh_from_db()
        self.assertTrue(self.session.is_completed)
        self.assertIsNotNone(self.session.completed_at)

    def test_submit_score_percentage(self):
        """2 questions : 1 bonne, 1 mauvaise → 50 %."""
        subject = Subject.objects.create(name='Multi Q')
        exam2 = Exam.objects.create(
            title='Exam 2Q', subject=subject, passing_score=60, created_by=self.user
        )
        q1 = Question.objects.create(exam=exam2, order=1, text='Q1')
        q2 = Question.objects.create(exam=exam2, order=2, text='Q2')
        c1 = Choice.objects.create(question=q1, text='Bonne', is_correct=True)
        Choice.objects.create(question=q1, text='Mauvaise', is_correct=False)
        Choice.objects.create(question=q2, text='Bonne', is_correct=True)
        c2_wrong = Choice.objects.create(question=q2, text='Mauvaise', is_correct=False)

        session2 = ExamSession.objects.create(user=self.user, exam=exam2)
        answers = {str(q1.id): [c1.id], str(q2.id): [c2_wrong.id]}
        result = ExamCorrectionService.submit_exam(session2, answers)
        self.assertEqual(result['score'], 50)
        self.assertEqual(result['total_questions'], 2)
