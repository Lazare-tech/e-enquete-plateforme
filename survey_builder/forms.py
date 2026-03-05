from django import forms

class DynamicSurveyForm(forms.Form):
    def __init__(self, survey, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.survey = survey
        
        # On boucle sur toutes les questions du questionnaire
        for question in survey.questions.all():
            field_key = f"question_{question.id}"
            label = question.label
            required = question.required
            
            # On choisit le type de champ Django selon le type en base de données
            if question.question_type == 'text':
                self.fields[field_key] = forms.CharField(label=label, required=required, widget=forms.TextInput(attrs={'class': 'form-control'}))
            
            elif question.question_type == 'number':
                self.fields[field_key] = forms.IntegerField(label=label, required=required, widget=forms.NumberInput(attrs={'class': 'form-control'}))
            
            elif question.question_type == 'date':
                self.fields[field_key] = forms.DateField(label=label, required=required, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
                
            elif question.question_type == 'select':
                # Pour le type "choix unique", on récupère les options liées (à créer plus tard)
                choices = [(opt.id, opt.text) for opt in question.options.all()]
                self.fields[field_key] = forms.ChoiceField(label=label, choices=choices, required=required, widget=forms.Select(attrs={'class': 'form-select'}))