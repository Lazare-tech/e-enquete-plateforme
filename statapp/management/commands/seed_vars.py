import random
import django
import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from statapp.models import VariableCategory, StatVariable
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Génère des données de test pour les variables statistiques'

    def handle(self, *args, **kwargs):
        self.stdout.write("Début du seeding...")

        # 1. Récupérer ou créer un utilisateur pour l'attribution
        user = User.objects.filter(is_staff=True).first()
        if not user:
            user = User.objects.create_superuser('admin_seed', 'admin@test.com', 'password123')
            self.stdout.write(f"Utilisateur créé : {user.username}")

        # 2. Définition des catégories
        categories_data = [
            "Démographie", 
            "Économie locale", 
            "Éducation", 
            "Santé Publique"
        ]

        categories_objs = []
        for cat_name in categories_data:
            cat, created = VariableCategory.objects.get_or_create(
                title=cat_name,
                defaults={'is_active': True} # Directement actives pour le test
            )
            categories_objs.append(cat)
            if created:
                self.stdout.write(f"Catégorie créée : {cat_name}")

        # 3. Liste de variables réalistes pour le Burkina Faso / contexte local
        variables_pool = [
            ("Taux d'alphabétisation", "41.2%"),
            ("Population estimée", "22 102 045"),
            ("Croissance PIB", "6.7%"),
            ("Taux de chômage (jeunes)", "15.4%"),
            ("Production de coton", "580 000 tonnes"),
            ("Nombre d'écoles primaires", "12 450"),
            ("Accès à l'eau potable", "76.8%"),
            ("Nombre de centres de santé", "1 840"),
            ("Inflation annuelle", "3.2%"),
            ("Exportation d'Or", "2 400 milliards FCFA"),
            ("Dette publique", "54% du PIB"),
            ("Taux de scolarisation", "88.5%"),
            ("Espérance de vie", "62 ans"),
            ("Nombre de lits d'hôpitaux", "12 pour 10 000 hab"),
            ("Consommation d'énergie", "450 kWh/hab"),
            ("Importations riz", "400 000 tonnes"),
            ("Nombre de diplômés/an", "45 000"),
            ("Taux de natalité", "36.5/1000"),
            ("Couverture vaccinale", "92%"),
            ("Indice de pauvreté", "40.1%")
        ]

        # 4. Création des 20 variables
        count = 0
        for label, value in variables_pool:
            StatVariable.objects.create(
                category=random.choice(categories_objs),
                label=label,
                value=value,
                created_by=user
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Succès ! {count} variables ont été injectées dans la base."))