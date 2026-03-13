from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Survey, Submission, Answer
from .forms import DynamicSurveyForm

#########################
@login_required # Force la connexion pour savoir qui remplit le formulaire
def fill_survey(request, uid):
    survey = get_object_or_404(Survey, uid=uid, is_active=True)
    questions = survey.questions.all().prefetch_related('options').order_by('order')
    
    if request.method == "POST":
        # On passe request.FILES pour capturer images et audios
        form = DynamicSurveyForm(survey, request.POST, request.FILES) 
        
        if form.is_valid():
            submission = Submission.objects.create(survey=survey, enumerator=request.user)
            
            for q in questions:
                # Ignorer les types qui ne sont pas des questions (Entete, section)
                if q.question_type in ['Entete', 'section']:
                    continue
                    
                field_name = f"question_{q.id}"
                valeur = form.cleaned_data.get(field_name)
                
                # Initialisation des données de réponse
                answer_data = {
                    "submission": submission,
                    "question": q,
                }

                # CAS 1 : Fichiers (Image ou Audio)
                if q.question_type in ['image', 'audio']:
                    if valeur: # 'valeur' contient ici un objet UploadedFile
                        answer_data["file_upload"] = valeur
                        answer_data["value"] = valeur.name # On garde le nom du fichier en texte par précaution
                
                # CAS 2 : Choix multiples (Checkbox)
                elif q.question_type == 'checkbox':
                    if isinstance(valeur, list):
                        answer_data["value"] = ", ".join(map(str, valeur))
                    else:
                        answer_data["value"] = str(valeur) if valeur else ""
                
                # CAS 3 : Autres types (text, textarea, number, select, date)
                else:
                    answer_data["value"] = str(valeur) if valeur else ""

                # Création de la réponse
                Answer.objects.create(**answer_data)

            return redirect('survey_builder:success')
    else:
        form = DynamicSurveyForm(survey)
        
    context = {
        'survey': survey,
        'questions': questions,
        'form': form # Important de passer le form au template
    }
    return render(request, 'survey_builder/fill_survey.html', context)
def survey_list(request):
    surveys = Survey.objects.filter(is_active=True)
    return render(request, 'survey_builder/list.html', {'surveys': surveys})
#
def survey_success(request):
    return render(request, 'survey_builder/success.html')
#############

