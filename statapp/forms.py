from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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