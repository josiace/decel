from django import forms
from .models import Course, TD, CorrectedTD
from skills.models import Subject


class CourseCreateForm(forms.ModelForm):
    """Formulaire de création de cours pour les contributeurs."""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'subject', 'content_type', 'content', 'content_file', 'dc_price', 'country', 'grade_level', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du cours'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description du cours'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Contenu du cours (si texte)'}),
            'content_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'dc_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': '0 pour gratuit'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'grade_level': forms.Select(attrs={'class': 'form-select'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CourseUpdateForm(forms.ModelForm):
    """Formulaire de modification de cours pour les contributeurs."""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'subject', 'content_type', 'content', 'content_file', 'dc_price', 'country', 'grade_level', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'content_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'dc_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'grade_level': forms.Select(attrs={'class': 'form-select'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TDCreateForm(forms.ModelForm):
    """Formulaire de création de TD pour les contributeurs."""
    
    class Meta:
        model = TD
        fields = ['title', 'description', 'subject', 'content_type', 'content', 'content_file', 'dc_price', 'country', 'grade_level', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du TD'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description du TD'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Contenu du TD (si texte)'}),
            'content_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'dc_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': '0 pour gratuit'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'grade_level': forms.Select(attrs={'class': 'form-select'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TDUpdateForm(forms.ModelForm):
    """Formulaire de modification de TD pour les contributeurs."""
    
    class Meta:
        model = TD
        fields = ['title', 'description', 'subject', 'content_type', 'content', 'content_file', 'dc_price', 'country', 'grade_level', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'content_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'dc_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'grade_level': forms.Select(attrs={'class': 'form-select'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CorrectedTDCreateForm(forms.ModelForm):
    """Formulaire de création de correction de TD pour les contributeurs."""
    
    class Meta:
        model = CorrectedTD
        fields = ['td', 'content_type', 'correction', 'correction_file', 'dc_price', 'country', 'grade_level']
        widgets = {
            'td': forms.Select(attrs={'class': 'form-select'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'correction': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Correction du TD (si texte)'}),
            'correction_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'dc_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': '0 pour gratuit'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'grade_level': forms.Select(attrs={'class': 'form-select'}),
        }


class CorrectedTDUpdateForm(forms.ModelForm):
    """Formulaire de modification de correction de TD pour les contributeurs."""
    
    class Meta:
        model = CorrectedTD
        fields = ['td', 'content_type', 'correction', 'correction_file', 'dc_price', 'country', 'grade_level']
        widgets = {
            'td': forms.Select(attrs={'class': 'form-select'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'correction': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'correction_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'dc_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'grade_level': forms.Select(attrs={'class': 'form-select'}),
        }
