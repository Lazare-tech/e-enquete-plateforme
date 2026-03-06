from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Survey, Submission, Answer
from .forms import DynamicSurveyForm

def fill_survey(request, uid):
    survey = get_object_or_404(Survey, uid=uid, is_active=True)
    
    if request.method == "POST":
        # Note : on ajoute request.FILES pour les photos
        form = DynamicSurveyForm(survey, request.POST, request.FILES) 
        
        if form.is_valid():
            submission = Submission.objects.create(survey=survey, enumerator=request.user)
            
            for q in survey.questions.all():
                field_name = f"question_{q.id}"
                valeur = form.cleaned_data.get(field_name)
                
                # CAS 1 : Choix multiples (on transforme la liste en texte séparé par des virgules)
                if q.question_type == 'checkbox' and isinstance(valeur, list):
                    valeur = ", ".join(valeur)
                
                # CAS 2 : Image (on peut créer un champ spécifique ou stocker le chemin)
                if q.question_type == 'image' and valeur:
                    # Ici, tu peux soit avoir un ImageField dans ton modèle Answer,
                    # soit gérer le stockage du fichier séparément.
                    pass 

                Answer.objects.create(
                    submission=submission,
                    question=q,
                    value=str(valeur) if valeur else ""
                )
            return redirect('survey_builder:success')
    else:
        form = DynamicSurveyForm(survey)

    return render(request, 'survey_builder/fill_survey.html', {'survey': survey, 'form': form})
#
def survey_list(request):
    surveys = Survey.objects.filter(is_active=True)
    return render(request, 'survey_builder/list.html', {'surveys': surveys})
#
def survey_success(request):
    return render(request, 'survey_builder/success.html')