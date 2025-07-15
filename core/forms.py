# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Rappel

class MedicalSignUpForm(UserCreationForm):
    """Formulaire d'inscription avec design médical et contraintes allégées"""
    
    # Champs personnalisés avec design médical
    username = forms.CharField(
        max_length=150,  # Augmenter la limite pour plus de flexibilité
        widget=forms.TextInput(attrs={
            'class': 'medical-input',
            'placeholder': 'Votre nom d\'utilisateur',
            'autocomplete': 'username'
        }),
        help_text='Choisissez le nom d\'utilisateur que vous voulez (max 150 caractères)',
        error_messages={
            'required': 'Le nom d\'utilisateur est requis.',
            'max_length': 'Le nom d\'utilisateur ne peut pas dépasser 150 caractères.'
        }
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'medical-input',
            'placeholder': 'votre.email@exemple.com',
            'autocomplete': 'email'
        })
    )
    
    first_name = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'medical-input',
            'placeholder': 'Votre prénom (optionnel)',
            'autocomplete': 'given-name'
        })
    )
    
    last_name = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'medical-input',
            'placeholder': 'Votre nom (optionnel)',
            'autocomplete': 'family-name'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'medical-input',
            'placeholder': 'Votre mot de passe',
            'autocomplete': 'new-password'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'medical-input',
            'placeholder': 'Confirmez votre mot de passe',
            'autocomplete': 'new-password'
        })
    )
    
    # Consentement médical
    medical_consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'medical-checkbox'}),
        label='J\'accepte que mes données soient utilisées pour améliorer les services médicaux'
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2", "medical_consent")
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Nettoyer le nom d'utilisateur
            username = username.strip()
            
            # Vérifier que le nom n'est pas vide après nettoyage
            if not username:
                raise forms.ValidationError('Le nom d\'utilisateur ne peut pas être vide.')
            
            # Vérification de l'unicité (insensible à la casse)
            if User.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError('Ce nom d\'utilisateur est déjà pris.')
            
            # Permettre n'importe quel caractère
            # Pas de validation de format spécifique
        
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # S'assurer que le nom d'utilisateur est correctement défini
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
        return user
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Cette adresse email est déjà utilisée.')
        return email

class MedicalLoginForm(forms.Form):
    """Formulaire de connexion avec design médical"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'medical-input',
            'placeholder': 'Nom d\'utilisateur ou email',
            'autocomplete': 'username',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'medical-input',
            'placeholder': 'Votre mot de passe',
            'autocomplete': 'current-password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'medical-checkbox'}),
        label='Se souvenir de moi'
    )

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse e-mail")
    first_name = forms.CharField(required=False, label="Prénom")
    last_name = forms.CharField(required=False, label="Nom")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

class RappelForm(forms.ModelForm):
    class Meta:
        model = Rappel
        fields = ["medicament", "heure"]
        widgets = {
            "heure": forms.TimeInput(format="%H:%M", attrs={"type": "time"})
        }