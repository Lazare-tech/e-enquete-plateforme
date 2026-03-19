from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify
import os
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
###################################################################
class Category(models.Model):
    """Permet de classer les données (ex: Économie, Santé, Démographie)"""
    title = models.CharField(max_length=100, verbose_name="Titre de la catégorie",unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(
        max_length=50, 
        default="fa-chart-bar", 
        help_text="Nom de la classe FontAwesome (ex: fa-user, fa-chart-line)"
    )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.title
class StatFile(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="files")
    title = models.CharField(max_length=255, verbose_name="Titre de l'enquête", null=True, blank=True)
    
    # AJOUTER CETTE LIGNE
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    
    description = models.TextField(verbose_name="Description détaillée", null=True, blank=True)
    authorized_users = models.ManyToManyField('auth.User', blank=True, related_name="allowed_stats")
    is_protected = models.BooleanField(default=True)
    file = models.FileField(upload_to='privatefold/stats_uploads/%Y/%m/', verbose_name="Fichier (CSV/Excel)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    download_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de téléchargements")
    is_active = models.BooleanField(default=False, verbose_name="Visible sur le site")
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Ajouté par"
    )

    # AJOUTER CETTE MÉTHODE POUR AUTO-GÉNÉRER LE SLUG
    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Sécurité anti-doublon pour le slug unique
            while StatFile.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower().replace('.', '')

    def __str__(self):
        return self.title if self.title else "Fichier sans titre"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Fichier statistique"
        verbose_name_plural = "Fichiers statistiques"
#############################################################################################
class VariableCategory(models.Model):
    title = models.CharField(max_length=100, unique=True, blank=True,null=True,verbose_name="Nom de la catégorie")
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name="Validée (Visible)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie de Variable"
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        # On définit une valeur de base (ton titre)
        label = self.title if self.title else "Sans titre"
        
        # On peut ajouter un indicateur visuel si ce n'est pas encore validé
        if not self.is_active:
            return f"{label} (En attente de validation)"
    
        return label
class StatVariable(models.Model):
    category = models.ForeignKey(VariableCategory, on_delete=models.CASCADE, related_name="variables")
    label = models.CharField(max_length=255, verbose_name="Nom de la variable")
    value = models.CharField(max_length=255, verbose_name="Valeur / Information")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ajouté par")
    ##
    class Meta:
        verbose_name = "Variable Statistique"
        verbose_name_plural = "Variables Statistiques"

    def __title__(self):
        return f"{self.label} : {self.value}"
############################################################
class UserFileAccess(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    stat_file = models.ForeignKey(StatFile, on_delete=models.CASCADE)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'stat_file') # Empêche les doublons
######

class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    is_active = models.BooleanField(default=True, verbose_name="Visible sur le site")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "FAQ"
        ordering = ['order', '-created_at'] # Tri par ordre, puis par date

    def __str__(self):
        return self.question
##########


class Document(models.Model):
    titre = models.CharField(max_length=255, verbose_name="Nom du document")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Notes / Description", blank=True)
    
    # Stockage physique sur le serveur
    fichier = models.FileField(
        upload_to='archives_agence/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'png', 'jpg'])],
        verbose_name="Fichier"
    )
    
    # Traçabilité
    date_upload = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    ajoute_par = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Agent responsable"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Document Agence"
        verbose_name_plural = "Documents Agence"
        ordering = ['-date_upload']

    def __str__(self):
        return self.titre
######################################
class ContactMessage(models.Model):
    nom = models.CharField(max_length=100) # Nouveau champ
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    objet = models.CharField(max_length=200)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.objet}"