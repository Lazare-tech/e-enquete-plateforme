from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Survey, Question, Option, Submission, Answer
from adminsortable2.admin import SortableAdminMixin, SortableTabularInline
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

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
    inlines = [QuestionInline] # On injecte les questions dans le formulaire Survey

@admin.register(Question)
class QuestionAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('order', 'label', 'survey', 'question_type')
    list_filter = ('survey',)
    inlines = [OptionInline]
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