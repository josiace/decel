from django import forms
from exams.models import Exam, Question, QuestionOption
from skills.models import Subject


class ExamCreateForm(forms.ModelForm):
    """Formulaire de création d'examen pour les contributeurs."""
    
    class Meta:
        model = Exam
        fields = ['title', 'description', 'subject', 'exam_type', 'question_file', 'difficulty', 'time_limit', 'passing_score']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l\'examen'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description de l\'examen'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'question_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'difficulty': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Laisser vide pour illimité'}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
        }


class QuestionCreateForm(forms.ModelForm):
    """Formulaire de création de question pour les contributeurs."""
    
    class Meta:
        model = Question
        fields = ['order']
        widgets = {
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class QuestionOptionForm(forms.ModelForm):
    """Formulaire de création d'option de question pour les contributeurs."""
    
    class Meta:
        model = QuestionOption
        fields = ['label', 'text', 'is_correct']
        widgets = {
            'label': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Texte de l\'option'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
