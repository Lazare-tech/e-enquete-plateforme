from django.urls import path
import survey_builder.views

app_name = 'survey_builder' # Pour utiliser {% url 'survey:fill' ... %}

urlpatterns = [
    # Cette URL attend l'ID du formulaire, par exemple : /survey/fill/1/
    path('fill/<int:survey_id>/', survey_builder.views.fill_survey, name='fill'),
    path('success/', survey_builder.views.survey_success, name='success'),
    path('forms', survey_builder.views.survey_list, name='list'),
]