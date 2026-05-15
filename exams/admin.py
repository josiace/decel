from django.contrib import admin
from .models import Exam, Question, Choice, ExamSession, UserAnswer, QuestionOption


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ['text', 'is_correct', 'order']


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4
    fields = ['label', 'text', 'is_correct', 'order']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['text', 'order']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'exam_type', 'subject', 'difficulty', 'question_count', 'is_active', 'created_at']
    list_filter = ['exam_type', 'subject', 'difficulty', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]
    fieldsets = (
        ('Informations de l\'examen', {'fields': ('title', 'description', 'subject'), 'description': 'Détails de l\'examen'}),
        ('Type d\'examen', {'fields': ('exam_type', 'question_file'), 'description': 'Choisir le type d\'examen et uploader le fichier PDF/image si nécessaire'}),
        ('Configuration', {'fields': ('difficulty', 'time_limit', 'passing_score'), 'description': 'Paramètres de l\'examen'}),
        ('Publication', {'fields': ('is_active',), 'description': 'Cocher pour rendre l\'examen disponible'}),
        ('Métadonnées', {'fields': ('created_by', 'created_at', 'updated_at'), 'description': 'Informations de création'}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['exam', 'text', 'order']
    list_filter = ['exam']
    search_fields = ['text']
    inlines = [ChoiceInline, QuestionOptionInline]
    fieldsets = (
        ('Question', {'fields': ('exam', 'text', 'order'), 'description': 'Énoncé de la question (vide si questions sur fichier)'}),
    )


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ['question', 'label', 'text', 'is_correct', 'order']
    list_filter = ['question', 'is_correct', 'label']
    search_fields = ['text', 'question__text']
    fieldsets = (
        ('Option de réponse', {'fields': ('question', 'label', 'text', 'is_correct', 'order'), 'description': 'Option de réponse pour une question sur fichier'}),
    )


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam', 'started_at', 'completed_at', 'score', 'passed', 'is_completed']
    list_filter = ['exam', 'is_completed', 'passed', 'started_at']
    search_fields = ['user__email', 'exam__title']
    readonly_fields = ['started_at', 'completed_at']
    fieldsets = (
        ('Session', {'fields': ('user', 'exam'), 'description': 'Utilisateur et examen'}),
        ('Horodatage', {'fields': ('started_at', 'completed_at'), 'description': 'Dates de début et de fin'}),
        ('Résultats', {'fields': ('score', 'passed', 'is_completed'), 'description': 'Score et statut'}),
    )


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'is_correct']
    list_filter = ['is_correct']
    search_fields = ['session__user__email']
    fieldsets = (
        ('Réponse', {'fields': ('session', 'question', 'selected_choices', 'selected_options'), 'description': 'Réponse de l\'utilisateur (choix ou options pour examens sur fichier)'}),
        ('Résultat', {'fields': ('is_correct',), 'description': 'Évaluation stricte QCM'}),
    )
