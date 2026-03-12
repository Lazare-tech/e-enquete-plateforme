import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from statapp.models import Category, StatFile  # Vérifie bien le nom de ton app

class Command(BaseCommand):
    help = 'Génère des catégories et des fichiers statistiques de test'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Début du remplissage de la base de données ---")

        # 1. Création d'un utilisateur Test (si inexistant)
        user, created = User.objects.get_or_create(
            username="admin_test", 
            defaults={
                "email": "admin@test.com",
                "is_staff": True,
                "is_superuser": True
            }
        )
        if created:
            user.set_password("password123")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Utilisateur {user.username} créé."))

        # 2. Définition des catégories
        categories_data = [
            {"title": "Agriculture", "icon": "fa-seedling"},
            {"title": "Démographie", "icon": "fa-users"},
            {"title": "Économie", "icon": "fa-chart-line"},
            {"title": "Santé", "icon": "fa-hand-holding-heart"},
            {"title": "Éducation", "icon": "fa-user-graduate"},
        ]

        categories_obj = {}
        for cat in categories_data:
            obj, created = Category.objects.get_or_create(
                title__iexact=cat['title'], 
                defaults={'title': cat['title'], 'icon': cat['icon']}
            )
            categories_obj[cat['title']] = obj
            if created:
                self.stdout.write(f"Catégorie créée : {cat['title']}")

        # 3. Définition des fichiers statistiques
        files_data = [
            {
                "category": "Agriculture",
                "title": "Production Agricole 2025",
                "desc": "Statistiques annuelles sur les rendements céréaliers...",
                "filename": "agriculture_2025.xlsx"
            },
            {
                "category": "Démographie",
                "title": "Recensement Population",
                "desc": "Données brutes du recensement général : répartition par âge...",
                "filename": "recensement_v1.csv"
            },
            {
                "category": "Économie",
                "title": "Indice des Prix (IPC)",
                "desc": "Évolution mensuelle du coût de la vie pour Q1 2026.",
                "filename": "ipc_2026_q1.xlsx"
            },
            {
                "category": "Éducation",
                "title": "Scolarisation Primaire",
                "desc": "Taux d'achèvement et de réussite au certificat d'études.",
                "filename": "education_stats.xlsx"
            },
            {
                "category": "Santé",
                "title": "Statistiques Sanitaires",
                "desc": "Rapport sur la couverture vaccinale au Burkina Faso.",
                "filename": "sante_nationale.csv"
            },
            {
                "category": "Agriculture",
                "title": "Exportations de Coton",
                "desc": "Volume et valeur des exportations filière coton 2025.",
                "filename": "coton_export.xlsx"
            }
        ]

        for data in files_data:
            # Simulation d'un fichier réel
            fake_content = ContentFile(b"Contenu de test genere par script.")
            
            # On cherche par titre
            stat, created = StatFile.objects.get_or_create(
                title__iexact=data['title'],
                defaults={
                    "title": data['title'],
                    "category": categories_obj[data['category']],
                    "description": data['desc'],
                    "is_protected": True,
                    "is_active": True,
                    "created_by": user # On oublie pas l'auteur !
                }
            )
            
            if created:
                # On enregistre le fichier physique
                stat.file.save(data['filename'], fake_content, save=True)
                self.stdout.write(self.style.SUCCESS(f"Fichier créé : {data['title']}"))
            else:
                self.stdout.write(f"Fichier déjà existant : {data['title']}")

        self.stdout.write(self.style.SUCCESS("--- Remplissage terminé avec succès ! ---"))