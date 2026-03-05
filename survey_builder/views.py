from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Survey, Submission, Answer
from .forms import DynamicSurveyForm

def fill_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, is_active=True)
    
    if request.method == "POST":
        form = DynamicSurveyForm(survey, request.POST)
        if form.is_valid():
            # 1. Créer la soumission parente
            submission = Submission.objects.create(survey=survey, enumerator=request.user)
            
            # 2. Enregistrer chaque réponse individuellement
            for question in survey.questions.all():
                field_key = f"question_{question.id}"
                valeur = form.cleaned_data.get(field_key)
                
                Answer.objects.create(
                    submission=submission,
                    question=question,
                    value=str(valeur) # On stocke tout en texte pour la flexibilité
                )
            return redirect('survey:success')
    else:
        form = DynamicSurveyForm(survey)

    return render(request, 'survey_builder/fill_survey.html', {'survey': survey, 'form': form})