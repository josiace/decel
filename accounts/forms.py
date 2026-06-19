from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Country


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone_number = forms.CharField(max_length=20, required=False, help_text="Numéro de téléphone (optionnel)")
    country = forms.ModelChoiceField(
        queryset=Country.objects.filter(is_active=True),
        required=False,
        empty_label="Sélectionnez votre pays",
        help_text="Pays de résidence (optionnel)"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'country', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.country = self.cleaned_data.get('country')
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulaire de connexion personnalisé qui utilise l'email au lieu du username.
    """
    username = forms.EmailField(label='Email', required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['username'].widget.attrs.update({'placeholder': 'Entrez votre email'})
