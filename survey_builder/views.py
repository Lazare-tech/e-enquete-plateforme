from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Survey, Submission, Answer
from .forms import DynamicSurveyForm
from django.db.models import Count
import json
from django.db import transaction # 

#########################
@login_required # Force la connexion pour savoir qui remplit le formulaire
def fill_survey(request, uid):
    survey = get_object_or_404(Survey, uid=uid, is_active=True)
    questions = survey.questions.all().prefetch_related('options').order_by('order')
    
    if request.method == "POST":
        # On passe request.FILES pour capturer images et audios
        form = DynamicSurveyForm(survey, request.POST, request.FILES) 
        
        if form.is_valid():
            try:
                with transaction.atomic():
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

                return redirect('survey_builder:success', survey.uid)
            except Exception as e:
                # En cas d'erreur de base de données, la transaction est annulée automatiquement
                form.add_error(None, f"Une erreur technique est survenue : {e}")
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
def survey_success(request,uid):
    survey = get_object_or_404(Survey, uid=uid)
    context = {
        "survey": survey  # On passe l'objet entier
    }

    return render(request, 'survey_builder/success.html', context)
#############

@staff_member_required
def survey_analytics(request, uid):
    survey = get_object_or_404(Survey, uid=uid)
    submissions = Submission.objects.filter(survey=survey)
    total_submissions = submissions.count() # Le total global du formulaire
    
    questions = survey.questions.exclude(question_type__in=['Entete', 'section']).order_by('order')
    all_stats = []
    
    for q in questions:
        # On récupère les valeurs brutes
        answers_qs = Answer.objects.filter(question=q).values_list('value', flat=True)
        # On filtre les réponses vides pour ne compter que les vrais remplissages
        answers = [a for a in answers_qs if a and str(a).strip()]
        
        # Nombre réel de personnes ayant répondu à CETTE question
        filled_count = len(answers)
        
        if filled_count == 0:
            continue

        display_type = 'pie'
        data = []
        
        # 1. CAS : CASES À COCHER
        if q.question_type == 'checkbox':
            display_type = 'bar'
            data_counts = {}
            for a in answers:
                parts = [p.strip() for p in str(a).split(',')]
                for choice in parts:
                    data_counts[choice] = data_counts.get(choice, 0) + 1
            data = [{'answer_value': k, 'count': v} for k, v in data_counts.items()]

        else:
            total_chars = sum(len(str(a)) for a in answers)
            avg_length = total_chars / filled_count
            unique_count = len(set(answers))

            if q.question_type == 'textarea' or avg_length > 60:
                display_type = 'paragraph'
                data = answers # On passe tout, le scroll du template gérera
            elif unique_count > (total_submissions * 0.8) and total_submissions > 3:
                display_type = 'text'
                data = answers
            elif q.question_type in ['text', 'number', 'date']:
                display_type = 'text'
                data = answers
            else:
                display_type = 'pie'
                data_counts = {}
                for a in answers:
                    data_counts[a] = data_counts.get(a, 0) + 1
                data = [{'answer_value': k, 'count': v} for k, v in data_counts.items()]

        all_stats.append({
            'label': q.label,
            'display_type': display_type,
            'data': data,
            'filled_count': filled_count  # <-- ON AJOUTE CELA ICI
        })

    return render(request, 'survey_builder/survey_analytics.html', {
        'all_stats': all_stats, 
        'survey': survey, 
        'total': total_submissions
    })