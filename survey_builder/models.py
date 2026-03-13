from django.db import models
from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.


class Survey(models.Model):
    """Le formulaire complet (ex: Enquête Nutrition 2026)"""
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True,verbose_name="Enquête visible sur le site")
    #
    class Meta:
        verbose_name = "Enquête"
        verbose_name_plural = "Enquêtes"

    def __str__(self):
        return self.title

class Question(models.Model):
    """Une question spécifique dans un formulaire"""
    TYPE_CHOICES = [
        ('Entete', '-- Titre illustratif(Regroupement)---'),
        ('section', 'Nouvelle section (Changement de page)'),
        ('text', 'Texte court'),
        ('textarea', 'Paragraphe (Texte long)'),
        ('number', 'Nombre'),
        ('select', 'Choix unique (Liste)'),
        ('checkbox', 'Choix multiples (Cases)'), 
        ('date', 'Date'),
        ('image', 'Photo/Image'),
        ('audio', 'Enregistrement audio'),
    ]
    
    survey = models.ForeignKey(Survey, related_name="questions", on_delete=models.CASCADE)
    label = models.CharField(max_length=500, verbose_name="Libellé de la question")
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, db_index=True) # Ajoute db_index pour la performance
    ##
    help_text = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Description / Aide",
        help_text="Texte descriptif qui s'affiche sous le titre ou la question."
    )
    # Si cette question dépend d'une autre :
    depends_on = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name="dependent_questions")
    # La valeur qui doit être répondue à "depends_on" pour afficher CETTE question
    dependency_value = models.CharField(max_length=255, blank=True, null=True, help_text="Valeur de l'option qui débloque cette question")
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        # Affiche le titre de l'enquête + le début de la question
        return f" {self.label[:50]}"

class Submission(models.Model):
    """Une instance de réponse (quand un enquêteur valide le formulaire)"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    enumerator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # Qui a rempli ?
    ####
    class Meta:
        verbose_name = "Soumission"
        verbose_name_plural = "Soumissions"
        ordering = ['-submitted_at'] # Les plus récentes en premier

    def __str__(self):
        return f"Soumission #{self.id} - {self.survey.title} ({self.submitted_at.strftime('%d/%m/%Y %H:%M')})"

    @property
    def response_count(self):
        return self.answers.count()
class Answer(models.Model):
    """La valeur d'une réponse pour une question donnée"""
    submission = models.ForeignKey(Submission, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.TextField() # On stocke tout en texte, à convertir selon le type
    ####
    file_upload = models.FileField(
        upload_to='enquete/responses/%Y/%m/', 
        blank=True, 
        null=True,
        verbose_name="Fichier joint (Image/Audio)"
    )
    def __str__(self):
        # Affiche la question et la réponse donnée
        return f"{self.question.label}"
##
class Option(models.Model):
    """Les choix pour les questions de type 'select'"""
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=200, verbose_name="Texte de l'option")
    value = models.CharField(max_length=50, verbose_name="Valeur technique (ex: M, F)")
    order = models.PositiveIntegerField(default=0, db_index=True)
    

    class Meta:
        verbose_name = "Option de réponse"
        verbose_name_plural = "Options de réponses"
        ordering = ['order']
        
    def __str__(self):
        return f"{self.text} ({self.value})"
########
# models.py
