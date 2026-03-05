from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import Category, StatFile, UserFileAccess

from django.test import TestCase, override_settings
import tempfile
import shutil

# On crée un dossier temporaire pour ne pas polluer vos vrais dossiers media
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class StatAppPermissionsTest(TestCase):
    
    @classmethod
    def tearDownClass(cls):
        # On supprime les fichiers de test après l'exécution
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()
    def setUp(self):
        # 1. Création des utilisateurs
        self.client = Client()
        self.user_authorized = User.objects.create_user(username='autorise', password='password123')
        self.user_unauthorized = User.objects.create_user(username='non_autorise', password='password123')
        
        # 2. Création de la catégorie (test du slug au passage)
        self.category = Category.objects.create(title="Économie Rurale")
        
        # 3. Création d'un fichier fictif
        self.dummy_file = SimpleUploadedFile(
            "test_data.xlsx", 
            b"content_of_the_excel_file", 
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        self.stat_file = StatFile.objects.create(
            category=self.category,
            title="Enquête Coton 2026",
            description="Données confidentielles sur la production de coton.",
            file=self.dummy_file,
            is_protected=True
        )
        
        # 4. Octroi de l'accès spécifique à l'utilisateur autorisé
        UserFileAccess.objects.create(user=self.user_authorized, stat_file=self.stat_file)

    def test_category_slug_generation(self):
        """Vérifie que le slug est bien généré automatiquement à partir du titre"""
        self.assertEqual(self.category.slug, "economie-rurale")

    def test_unauthorized_access_denied(self):
        """Vérifie qu'un utilisateur non autorisé reçoit une erreur ou un refus (403)"""
        self.client.login(username='non_autorise', password='password123')
        
        # On suppose que l'URL de téléchargement s'appelle 'statapp:download'
        url = reverse('statapp:download', kwargs={'file_id': self.stat_file.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 403)
    def test_authorized_access_allowed(self):
        """Vérifie qu'un utilisateur avec UserFileAccess peut télécharger le fichier"""
        self.client.login(username='autorise', password='password123')
        
        url = reverse('statapp:download', kwargs={'file_id': self.stat_file.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)

        # CORRECTION : On joint le flux de données pour comparer le contenu
        content = b"".join(response.streaming_content)
        self.assertEqual(content, b"content_of_the_excel_file")
    def test_download_counter_increments(self):
        """Vérifie que le compteur de téléchargement augmente après un succès"""
        initial_count = self.stat_file.download_count # Vaut 0
        self.client.login(username='autorise', password='password123')
        
        url = reverse('statapp:download', kwargs={'file_id': self.stat_file.id})
        self.client.get(url)
        
        # CRUCIAL : Rafraîchir l'instance depuis la DB
        self.stat_file.refresh_from_db() 
        
        self.assertEqual(self.stat_file.download_count, initial_count + 1)