from django.contrib import admin
from .models import Category, StatFile, UserFileAccess,FAQ
from django.contrib.auth.models import User
from django import forms
from adminsortable2.admin import SortableAdminMixin
from openpyxl.styles import Font, Alignment, PatternFill
import openpyxl
##################33
# 1. Création d'un formulaire personnalisé pour l'accès
class UserFileAccessForm(forms.ModelForm):
    # On redéfinit le champ user pour changer son étiquette
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Utilisateur (Email)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On remplace l'affichage par défaut (username) par l'email
        self.fields['user'].label_from_instance = lambda obj: f"{obj.email} ({obj.username})" if obj.email else obj.username

    class Meta:
        model = UserFileAccess
        fields = '__all__'
# 1. Permet d'ajouter/voir les utilisateurs autorisés directement dans la page du fichier
class UserFileAccessInline(admin.TabularInline):
    model = UserFileAccess
    extra = 1  # Affiche une ligne vide par défaut pour ajouter un utilisateur rapidement

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'icon')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)

@admin.register(StatFile)
class StatFileAdmin(admin.ModelAdmin):
    # Ajout du slug dans l'affichage
    list_display = ('title', 'category', 'slug', 'download_count', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)
    
    # Génère le slug automatiquement pendant que tu tapes le titre
    prepopulated_fields = {'slug': ('title',)}
    
    # Intégration de l'Inline pour gérer les accès WhatsApp en un clic
    inlines = [UserFileAccessInline]

    fieldsets = (
        ('Informations Générales', {
            'fields': ('category', 'title', 'slug', 'description', 'is_active', 'is_protected')
        }),
        ('Fichier & Données', {
            'fields': ('file', 'download_count'),
        }),
        ('Dates (Lecture seule)', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Cache cette section par défaut
        }),
    )
    
    readonly_fields = ('download_count', 'created_at', 'updated_at')

# 2. Enregistrer aussi le modèle d'accès séparément pour une vue d'ensemble
@admin.register(UserFileAccess)
class UserFileAccessAdmin(admin.ModelAdmin):
    form = UserFileAccessForm # On applique le formulaire ici
    list_display = ('user_email', 'stat_file', 'granted_at')
    list_filter = ('granted_at', 'stat_file')
    search_fields = ('user__email', 'user__username', 'stat_file__title')
    #
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email de l\'utilisateur'
#####
@admin.register(FAQ)
class FAQAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('order', 'question', 'is_active')
    list_editable = ('is_active',) # Permet de masquer une question d'un clic
    search_fields = ('question', 'answer')