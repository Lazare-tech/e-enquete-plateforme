import os
import django
from django.core.files.base import ContentFile
from django.utils.text import slugify

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') # Remplacez 'core' par le nom de votre dossier de config
django.setup()

from django.contrib.auth.models import User
from statapp.models import Category, StatFile # Remplacez 'statapp' par le nom de votre application

def run():
    print("--- Début du remplissage de la base de données ---")

    # 1. Création d'un utilisateur Test (si inexistant)
    user, created = User.objects.get_or_create(username="admin_test", email="admin@test.com")
    if created:
        user.set_password("password123")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"Utilisateur {user.username} créé.")

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
        obj, _ = Category.objects.get_or_create(title=cat['title'], defaults={'icon': cat['icon']})
        categories_obj[cat['title']] = obj
    print("Catégories créées.")

    # 3. Définition des 6 fichiers statistiques
    files_data = [
        {
            "category": "Agriculture",
            "title": "Production Agricole 2025",
            "desc": "Statistiques annuelles sur les rendements céréaliers, la pluviométrie et l'utilisation des intrants par région.",
            "filename": "agriculture_2025.xlsx"
        },
        {
            "category": "Démographie",
            "title": "Recensement Population",
            "desc": "Données brutes du recensement général : répartition par âge, sexe et zone géographique (Urbain/Rural).",
            "filename": "recensement_v1.csv"
        },
        {
            "category": "Économie",
            "title": "Indice des Prix (IPC)",
            "desc": "Évolution mensuelle du coût de la vie et panier de la ménagère pour le premier trimestre 2026.",
            "filename": "ipc_2026_q1.xlsx"
        },
        {
            "category": "Éducation",
            "title": "Scolarisation Primaire",
            "desc": "Taux d'achèvement et de réussite au certificat d'études primaires par province et par genre.",
            "filename": "education_stats.xlsx"
        },
        {
            "category": "Santé",
            "title": "Statistiques Sanitaires",
            "desc": "Rapport sur la couverture vaccinale et la fréquentation des centres de santé communautaires au Burkina Faso.",
            "filename": "sante_nationale.csv"
        },
        {
            "category": "Agriculture",
            "title": "Exportations de Coton",
            "desc": "Volume et valeur des exportations de la filière coton vers les marchés internationaux pour la campagne 2025.",
            "filename": "coton_export.xlsx"
        }
    ]

    for data in files_data:
        # On simule un fichier réel avec ContentFile
        fake_content = ContentFile(b"Ceci est un fichier de test genere par script.")
        
        stat, created = StatFile.objects.get_or_create(
            title=data['title'],
            defaults={
                "category": categories_obj[data['category']],
                "description": data['desc'],
                "is_protected": True,
                "is_active": True
            }
        )
        if created:
            stat.file.save(data['filename'], fake_content, save=True)
            print(f"Fichier créé : {data['title']}")

    print("--- Remplissage terminé avec succès ! ---")

if __name__ == "__main__":
    run()