from django.db import models
from django.conf import settings
from skills.models import Subject


class Exam(models.Model):
    """
    Modèle d'examen - représente un examen complet avec plusieurs questions.
    Lié à une matière pour le suivi des compétences.
    """
    EXAM_TYPE_CHOICES = [
        ('manual', 'Questions saisies manuellement'),
        ('file', 'Questions sur fichier (PDF/Image)'),
    ]
    
    title = models.CharField(max_length=255, verbose_name="Titre", help_text="Titre de l'examen")
    description = models.TextField(blank=True, verbose_name="Description", help_text="Description détaillée de l'examen")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams', verbose_name="Matière", help_text="Matière associée à l'examen")
    
    # Exam type
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='manual', verbose_name="Type d'examen", help_text="Type d'examen : questions manuelles ou sur fichier")
    
    # File for questions (PDF or image)
    question_file = models.FileField(upload_to='exams/questions/', null=True, blank=True, verbose_name="Fichier de questions", help_text="Fichier PDF ou image contenant les questions (si type = fichier)")
    
    # Difficulty level (1-5)
    difficulty = models.IntegerField(default=1, verbose_name="Difficulté", help_text="Niveau de difficulté (1=Facile, 5=Difficile)")
    
    # Time limit in minutes (null = no limit)
    time_limit = models.IntegerField(null=True, blank=True, verbose_name="Limite de temps", help_text="Limite de temps en minutes (laisser vide pour illimité)")
    
    # Passing score percentage
    passing_score = models.IntegerField(default=60, verbose_name="Score de passage", help_text="Pourcentage minimum pour réussir l'examen")
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Créé par", help_text="Utilisateur qui a créé l'examen")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    is_active = models.BooleanField(default=True, verbose_name="Actif", help_text="Cocher pour rendre l'examen disponible aux utilisateurs")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Examen"
        verbose_name_plural = "Examens"
    
    def __str__(self):
        return self.title
    
    def question_count(self):
        return self.questions.count()


class Question(models.Model):
    """
    Modèle de question - question individuelle dans un examen.
    Supporte les questions à choix multiples (QCM) et les questions sur fichier.
    """
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions', verbose_name="Examen", help_text="Examen auquel cette question appartient")
    text = models.TextField(blank=True, verbose_name="Énoncé", help_text="Énoncé de la question (vide si questions sur fichier)")
    order = models.IntegerField(default=0, verbose_name="Ordre", help_text="Ordre d'affichage de la question")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Question"
        verbose_name_plural = "Questions"
    
    def __str__(self):
        if self.text:
            return f"Q{self.order}: {self.text[:50]}..."
        return f"Q{self.order}: Question sur fichier"


class QuestionOption(models.Model):
    """
    Modèle d'option de réponse pour les questions sur fichier.
    Permet à l'admin d'ajouter visuellement des options (A, B, C, D, etc.) et de cocher les correctes.
    """
    QUESTION_LABEL_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
    ]
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', verbose_name="Question", help_text="Question à laquelle cette option appartient")
    label = models.CharField(max_length=10, choices=QUESTION_LABEL_CHOICES, verbose_name="Label", help_text="Label de l'option (A, B, C, D, 1, 2, 3, etc.)")
    text = models.CharField(max_length=500, verbose_name="Texte de l'option", help_text="Texte de l'option de réponse")
    is_correct = models.BooleanField(default=False, verbose_name="Réponse correcte", help_text="Cocher si cette option est une bonne réponse")
    order = models.IntegerField(default=0, verbose_name="Ordre", help_text="Ordre d'affichage de l'option")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Option de réponse"
        verbose_name_plural = "Options de réponse"
    
    def __str__(self):
        return f"{self.label}: {self.text}"


class Choice(models.Model):
    """
    Modèle de choix - réponses possibles pour une question.
    Au moins un choix doit être marqué comme correct.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name="Question", help_text="Question à laquelle ce choix appartient")
    text = models.CharField(max_length=500, verbose_name="Texte", help_text="Texte de la réponse")
    is_correct = models.BooleanField(default=False, verbose_name="Correct", help_text="⚠️ Cocher SEULEMENT pour les bonnes réponses")
    order = models.IntegerField(default=0, verbose_name="Ordre", help_text="Ordre d'affichage du choix")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Choix de réponse"
        verbose_name_plural = "Choix de réponses"
    
    def __str__(self):
        return self.text


class ExamSession(models.Model):
    """
    Modèle de session d'examen - suit la tentative d'un utilisateur à un examen.
    Stocke l'heure de début, l'heure de fin et le score final.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_sessions', verbose_name="Utilisateur", help_text="Utilisateur qui a passé l'examen")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sessions', verbose_name="Examen", help_text="Examen passé")
    
    # Session tracking
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Heure de début")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Heure de fin")
    
    # Results
    score = models.IntegerField(null=True, blank=True, verbose_name="Score", help_text="Score en pourcentage")
    passed = models.BooleanField(null=True, blank=True, verbose_name="Réussi", help_text="Indique si l'examen a été réussi")
    
    # Status
    is_completed = models.BooleanField(default=False, verbose_name="Terminé", help_text="Indique si la session est terminée")
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ['user', 'exam']  # One active session per user per exam
        verbose_name = "Session d'examen"
        verbose_name_plural = "Sessions d'examen"
    
    def __str__(self):
        return f"{self.user.email} - {self.exam.title}"


class UserAnswer(models.Model):
    """
    Modèle de réponse utilisateur - stocke les choix sélectionnés par l'utilisateur pour chaque question.
    Utilisé pour l'évaluation stricte des QCM.
    """
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers', verbose_name="Session", help_text="Session d'examen associée")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Question", help_text="Question répondue")
    selected_choices = models.ManyToManyField(Choice, related_name='user_answers', blank=True, verbose_name="Choix sélectionnés", help_text="Choix de réponse sélectionnés par l'utilisateur (pour examens manuels)")
    
    # For file-based exams: selected answer options (A, B, C, D, etc.)
    selected_options = models.ManyToManyField(QuestionOption, related_name='user_answers', blank=True, verbose_name="Options sélectionnées", help_text="Options de réponse sélectionnées par l'utilisateur (pour examens sur fichier)")
    
    # Result of strict evaluation
    is_correct = models.BooleanField(default=False, verbose_name="Correct", help_text="Indique si la réponse est correcte (évaluation stricte)")
    
    class Meta:
        unique_together = ['session', 'question']
        verbose_name = "Réponse utilisateur"
        verbose_name_plural = "Réponses utilisateurs"
    
    def __str__(self):
        return f"Session {self.session.id} - Q{self.question.order}"
