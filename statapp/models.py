from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify
import os

class Category(models.Model):
    """Permet de classer les données (ex: Économie, Santé, Démographie)"""
    title = models.CharField(max_length=100, verbose_name="Titre de la catégorie")
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
    is_active = models.BooleanField(default=True, verbose_name="Visible sur le site")

    # AJOUTER CETTE MÉTHODE POUR AUTO-GÉNÉRER LE SLUG
    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower().replace('.', '')

    def __str__(self):
        return self.title if self.title else "Fichier sans titre"

    class Meta:
        ordering = ['-created_at']
############################################################
class UserFileAccess(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    stat_file = models.ForeignKey(StatFile, on_delete=models.CASCADE)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'stat_file') # Empêche les doublons