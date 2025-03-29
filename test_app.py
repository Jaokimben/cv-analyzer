import os
import unittest
import tempfile
import shutil
from app import app
from storage_manager import StorageManager
from cv_processor import CVProcessor

class CVAnalyzerTestCase(unittest.TestCase):
    """Tests pour l'application CV Analyzer"""

    def setUp(self):
        """Configuration avant chaque test"""
        # Configurer l'application en mode test
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        # Créer des répertoires temporaires pour les tests
        self.temp_dir = tempfile.mkdtemp()
        self.upload_dir = os.path.join(self.temp_dir, 'uploads')
        self.download_dir = os.path.join(self.temp_dir, 'downloads')
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Configurer l'application pour utiliser ces répertoires
        app.config['UPLOAD_FOLDER'] = self.upload_dir
        app.config['DOWNLOAD_FOLDER'] = self.download_dir
        
        # Créer un client de test
        self.client = app.test_client()
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        # Supprimer les répertoires temporaires
        shutil.rmtree(self.temp_dir)
    
    def test_index_page(self):
        """Test de la page d'accueil"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CV Analyzer', response.data)
        self.assertIn(b'Adaptez votre CV', response.data)
    
    def test_storage_manager(self):
        """Test du gestionnaire de stockage"""
        storage = StorageManager()
        
        # Vérifier que les chemins sont corrects
        self.assertTrue(os.path.exists(storage.get_upload_path()))
        self.assertTrue(os.path.exists(storage.get_download_path()))
        
        # Vérifier la génération de chemins de fichiers
        test_filename = "test_file.docx"
        upload_path = storage.get_upload_file_path(test_filename)
        download_path = storage.get_download_file_path(test_filename)
        
        self.assertIn("uploads", str(upload_path))
        self.assertIn("downloads", str(download_path))
        self.assertIn(test_filename, str(upload_path))
        self.assertIn(test_filename, str(download_path))
    
    def test_cv_processor_keyword_extraction(self):
        """Test de l'extraction de mots-clés"""
        processor = CVProcessor(self.upload_dir, self.download_dir)
        
        # Description de poste de test
        job_description = """
        Développeur Python Senior
        
        Nous recherchons un développeur Python expérimenté pour rejoindre notre équipe.
        
        Responsabilités:
        - Développer des applications web avec Flask et Django
        - Travailler sur des projets d'intelligence artificielle
        - Collaborer avec l'équipe de data scientists
        
        Compétences requises:
        - 5+ ans d'expérience en Python
        - Connaissance de Flask et Django
        - Expérience en développement web
        - Familiarité avec les concepts d'IA et de machine learning
        """
        
        # Extraire les mots-clés
        keywords = processor.extract_keywords_from_job_description(job_description)
        
        # Vérifier que les mots-clés importants sont extraits
        self.assertIsInstance(keywords, dict)
        
        # Aplatir tous les mots-clés pour faciliter la vérification
        all_keywords = []
        for category, words in keywords.items():
            all_keywords.extend(words.keys())
        
        # Vérifier la présence de mots-clés importants
        important_keywords = ["python", "développeur", "flask", "django", "expérience"]
        for keyword in important_keywords:
            self.assertIn(keyword, all_keywords)
    
    def test_error_pages(self):
        """Test des pages d'erreur"""
        # Test de la page 404
        response = self.client.get('/page_inexistante')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page non trouv', response.data)
        
        # Note: Tester la page 500 nécessiterait de provoquer une erreur serveur

if __name__ == '__main__':
    unittest.main()
