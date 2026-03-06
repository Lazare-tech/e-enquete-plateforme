from django.contrib import admin
import csv
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from django.http import HttpResponse
from datetime import datetime
# Register your models here.
from django.contrib import admin
from .models import Survey, Question, Option, Submission, Answer
from adminsortable2.admin import SortableAdminMixin, SortableTabularInline
from django.utils.html import format_html
from django.urls import reverse
# 1. Permet d'ajouter des options directement sous la question
class OptionInline(SortableTabularInline):
    model = Option
    extra = 1

# 2. Permet d'ajouter des questions directement sous le questionnaire
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True # Permet d'ouvrir la question en grand si besoin
    fieldsets = (
        (None, {
            'fields': (('label', 'question_type'), ('required', 'order'))
        }),
    )
###########################################
def export_survey_to_csv(modeladmin, request, queryset):
    # On prend le premier questionnaire sélectionné pour l'exemple
    # (Ou on boucle si on veut fusionner, mais l'export par questionnaire est plus logique)
    for survey in queryset:
        response = HttpResponse(content_type='text/csv')
        # Nom du fichier dynamique : ex_recensement_eau_2026-03-06.csv
        filename = f"export_{survey.title.lower().replace(' ', '_')}_{datetime.now().strftime('%Y-%m-%d')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        
        # 1. Préparation des En-têtes (Colonnes)
        questions = survey.questions.all().order_by('order')
        headers = ['ID Soumission', 'Date', 'Enquêteur'] + [q.label for q in questions]
        writer.writerow(headers)
        
        # 2. Récupération des données (Lignes)
        submissions = Submission.objects.filter(survey=survey).prefetch_related('answers')
        
        for sub in submissions:
            row = [sub.id, sub.submitted_at.strftime("%d/%m/%Y %H:%M"), sub.enumerator.username if sub.enumerator else "Anonyme"]
            
            # Pour chaque question du questionnaire, on cherche la réponse correspondante
            answers_dict = {a.question_id: a.value for a in sub.answers.all()}
            for q in questions:
                row.append(answers_dict.get(q.id, "")) # On met vide si pas de réponse
            
            writer.writerow(row)
            
        return response # Renvoie le fichier pour le premier survey coché

export_survey_to_csv.short_description = "Exporter les réponses en CSV"
####
def export_survey_to_excel(modeladmin, request, queryset):
    # On crée un nouveau classeur Excel
    wb = openpyxl.Workbook()
    
    for survey in queryset:
        # On crée une feuille par questionnaire (ou on utilise la première)
        ws = wb.active
        ws.title = "Réponses"
        
        # --- STYLE DES EN-TÊTES ---
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="122046", end_color="122046", fill_type="solid") # Bleu Shine
        alignment = Alignment(horizontal="center", vertical="center")

        # 1. PRÉPARATION DES COLONNES
        questions = survey.questions.all().order_by('order')
        headers = ['ID', 'Date de soumission', 'Enquêteur'] + [q.label for q in questions]
        
        # Écriture des en-têtes
        ws.append(headers)
        
        # Appliquer le style aux en-têtes
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = alignment

        # 2. RÉCUPÉRATION DES DONNÉES
        submissions = Submission.objects.filter(survey=survey).prefetch_related('answers')
        
        for sub in submissions:
            row = [
                sub.id, 
                sub.submitted_at.strftime("%d/%m/%Y %H:%M"), 
                sub.enumerator.username if sub.enumerator else "Anonyme"
            ]
            
            # On crée un dictionnaire {question_id: valeur} pour un accès rapide
            answers_dict = {a.question_id: a.value for a in sub.answers.all()}
            
            for q in questions:
                row.append(answers_dict.get(q.id, "")) # On ajoute la réponse ou vide
            
            ws.append(row)

        # Ajuster la largeur des colonnes automatiquement
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except: pass
            ws.column_dimensions[column].width = max_length + 2

    # Préparation de la réponse HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"export_{datetime.now().strftime('%Y%md_%H%M')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response

export_survey_to_excel.short_description = "Exporter en Excel (.xlsx)"
@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title','share_link', 'created_by', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
    actions = [export_survey_to_csv, export_survey_to_excel] # Ajout de l'action ici
    inlines = [QuestionInline] # On injecte les questions dans le formulaire Survey
    #
    def share_link(self, obj):
        # On construit l'URL complète
        url = reverse('survey_builder:fill', kwargs={'uid': obj.uid})
        # Note : En admin, on utilise souvent le domaine par défaut ou request
        full_url = f"http://127.0.0.1:8000{url}" # À adapter selon ton domaine de prod
        
        # Le HTML du bouton "Copier" avec un petit script intégré
        return format_html(
            '''
            <div style="display:flex; align-items:center;">
                <input type="text" value="{}" id="url_{}" style="width:1px; opacity:0; position:absolute;">
                <button type="button" onclick="copyToClipboard('url_{}')" 
                        style="background:#122046; color:white; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:10px;">
                    <i class="fas fa-copy"></i> Copier le lien
                </button>
                <script>
                    function copyToClipboard(id) {{
                        var copyText = document.getElementById(id);
                        navigator.clipboard.writeText(copyText.value);
                        alert("Lien copié dans le presse-papier !");
                    }}
                </script>
            </div>
            ''',
            full_url, obj.id, obj.id
        )

    share_link.short_description = "Partage"
    class Media:
        js = ('js/admin_cp.js',)
    ####
 
from django.contrib.admin import SimpleListFilter

@admin.register(Question)
class QuestionAdmin(SortableAdminMixin, admin.ModelAdmin):
    # On affiche clairement à quel formulaire appartient la question
    list_display = ('label', 'survey_name', 'order', 'question_type')
    
    # On force le filtre sur le Survey uniquement
    # 'admin.RelatedOnlyFieldListFilter' permet de ne montrer que les 
    # formulaires qui possèdent réellement des questions.
    list_filter = (
        ('survey', admin.RelatedOnlyFieldListFilter),
        'question_type',
    )
    
    # Recherche par nom de formulaire pour filtrer au clavier
    search_fields = ('label', 'survey__title')
    
    ordering = ('survey', 'order')

    def survey_name(self, obj):
        return obj.survey.title
    survey_name.short_description = "Formulaire"
# Visualisation des réponses (Lecture seule pour la sécurité des données)
class AnswerInline(admin.TabularInline):
    model = Answer
    readonly_fields = ('question', 'value')
    extra = 0
    can_delete = False

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('survey', 'enumerator', 'submitted_at')
    readonly_fields = ('survey', 'enumerator', 'submitted_at')
    inlines = [AnswerInline]
