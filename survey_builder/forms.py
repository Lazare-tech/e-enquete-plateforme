from django import forms

from django import forms
###########################################################
class DynamicSurveyForm(forms.Form):
    def __init__(self, survey, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # On boucle sur les questions triées par 'order' (grâce au Meta du modèle)
        for question in survey.questions.all():
            field_key = f"question_{question.id}"
            label = question.label
            required = question.required
            
            # --- 1. LOGIQUE POUR LES CHOIX (Select, Radio, Checkbox) ---
            if question.question_type in ['select', 'radio', 'checkbox']:
                choices = [(opt.value, opt.text) for opt in question.options.all()]
                
                if question.question_type == 'select':
                    self.fields[field_key] = forms.ChoiceField(
                        label=label, choices=choices, required=required,
                        widget=forms.Select(attrs={'class': 'form-select'})
                    )
                elif question.question_type == 'radio':
                    self.fields[field_key] = forms.ChoiceField(
                        label=label, choices=choices, required=required,
                        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
                    )
                elif question.question_type == 'checkbox':
                    self.fields[field_key] = forms.MultipleChoiceField(
                        label=label, choices=choices, required=required,
                        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
                    )

            # --- 2. TYPES DE SAISIE DIRECTE ---
            elif question.question_type == 'text':
                self.fields[field_key] = forms.CharField(
                    label=label, required=required, 
                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Réponse courte'})
                )
            
            elif question.question_type == 'textarea': # Pour les paragraphes
                self.fields[field_key] = forms.CharField(
                    label=label, required=required, 
                    widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Votre message ici...'})
                )
            
            elif question.question_type == 'number':
                self.fields[field_key] = forms.IntegerField(
                    label=label, required=required, 
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )

            elif question.question_type == 'date':
                self.fields[field_key] = forms.DateField(
                    label=label, required=required,
                    widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
                )
#######################
