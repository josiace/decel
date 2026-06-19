from django.contrib import admin
from .models import Exam, Question, Choice, ExamSession, UserAnswer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ['label', 'text', 'is_correct', 'order']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['text', 'order']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'exam_type', 'subject', 'difficulty', 'question_count', 'is_active', 'created_by', 'created_at']
    list_filter = ['exam_type', 'subject', 'difficulty', 'is_active', 'created_by', 'created_at']
    search_fields = ['title', 'description', 'created_by__email']
    inlines = [QuestionInline]
    fieldsets = (
        ('Informations de l\'examen', {'fields': ('title', 'description', 'subject'), 'description': 'Détails de l\'examen'}),
        ('Type d\'examen', {'fields': ('exam_type', 'question_file'), 'description': 'Choisir le type d\'examen et uploader le fichier PDF/image si nécessaire'}),
        ('Configuration', {'fields': ('difficulty', 'time_limit', 'passing_score'), 'description': 'Paramètres de l\'examen'}),
        ('Système XP', {'fields': ('xp_per_correct', 'xp_penalty_per_wrong', 'xp_reward_for_contributor'), 'description': 'Configuration des XP'}),
        ('Publication', {'fields': ('is_active',), 'description': 'Cocher pour rendre l\'examen disponible'}),
        ('Métadonnées', {'fields': ('created_by', 'created_at', 'updated_at'), 'description': 'Informations de création'}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['exam', 'text', 'order']
    list_filter = ['exam']
    search_fields = ['text']
    inlines = [ChoiceInline]
    fieldsets = (
        ('Question', {'fields': ('exam', 'text', 'order'), 'description': 'Énoncé de la question (vide si questions sur fichier)'}),
    )


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'label', 'text', 'is_correct', 'order']
    list_filter = ['question', 'is_correct', 'label']
    search_fields = ['text', 'question__text']
    fieldsets = (
        ('Choix de réponse', {'fields': ('question', 'label', 'text', 'is_correct', 'order'), 'description': 'Choix de réponse pour une question (label optionnel pour questions sur fichier)'}),
    )


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam', 'started_at', 'completed_at', 'score', 'passed', 'is_completed', 'is_best_attempt', 'xp_earned']
    list_filter = ['exam', 'is_completed', 'passed', 'is_best_attempt', 'started_at']
    search_fields = ['user__email', 'exam__title']
    readonly_fields = ['started_at', 'completed_at']
    fieldsets = (
        ('Session', {'fields': ('user', 'exam'), 'description': 'Utilisateur et examen'}),
        ('Horodatage', {'fields': ('started_at', 'completed_at'), 'description': 'Dates de début et de fin'}),
        ('Résultats', {'fields': ('score', 'passed', 'is_completed', 'is_best_attempt', 'xp_earned'), 'description': 'Score et statut'}),
    )


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'is_correct']
    list_filter = ['is_correct']
    search_fields = ['session__user__email']
    fieldsets = (
        ('Réponse', {'fields': ('session', 'question', 'selected_choices'), 'description': 'Réponse de l\'utilisateur'}),
        ('Résultat', {'fields': ('is_correct',), 'description': 'Évaluation stricte QCM'}),
    )
