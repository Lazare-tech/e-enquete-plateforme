from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StatFile, StatVariable,VariableCategory,ContactMessage,Newsletter
from django.urls import reverse_lazy

###############
class CleanRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Utilisé pour activer vos accès aux fichiers.")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None
            field.widget.attrs.update({'class': 'form-control rounded-pill'})
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email") # Tu peux ajouter "first_name", etc.
######################33


class StatFileForm(forms.ModelForm):
    class Meta:
        model = StatFile
        fields = ['category', 'title', 'description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On rend la catégorie non-obligatoire dans le FORMULAIRE uniquement
        self.fields['category'].required = False

class StatVariableForm(forms.ModelForm):
    # On ajoute un champ qui n'est pas dans le modèle pour la nouvelle catégorie
    

    class Meta:
        model = StatVariable
        fields = ['category', 'label', 'value']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le champ category optionnel dans le formulaire uniquement
        self.fields['category'].required = False
        # On ne montre que les catégories déjà activées par l'admin dans le dropdown
        self.fields['category'].queryset = VariableCategory.objects.filter(is_active=True)
#################################################
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['nom', 'email', 'telephone', 'objet', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom complet'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre téléphone'}),
            'objet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objet du message'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message', 'rows': 4}),
        }
###############################
class NewsLetterForm(forms.ModelForm):
    email = forms.EmailField(
        label="Votre adresse email",
        error_messages={
            'invalid': "Veuillez entrer une adresse email valide (ex: contact@domaine.com).",
            'required': "L'email est nécessaire pour s'abonner.",
            'unique': "Cette adresse email est déjà inscrite à notre newsletter."
        },
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre email...',
            'id': 'newsletter-email'
        })
    )

    class Meta:
        model = Newsletter
        # On ne demande que l'email, le slug et la date sont gérés automatiquement
        fields = ['email']

    def clean_email(self):
        """Vérifie si l'email existe déjà pour éviter les doublons proprement"""
        email = self.cleaned_data.get('email').lower() # On passe tout en minuscule
        if Newsletter.objects.filter(email=email).exists():
            raise forms.ValidationError("Vous êtes déjà inscrit à notre newsletter !")
        return email
    
    