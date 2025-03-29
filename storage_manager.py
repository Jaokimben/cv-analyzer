import os
import logging
from pathlib import Path

class StorageManager:
    """
    Gestionnaire de stockage pour l'application CV Analyzer.
    Gère le stockage persistant pour les fichiers téléchargés et générés,
    compatible avec le déploiement sur Railway.app et Render.com.
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire de stockage avec les chemins appropriés
        selon l'environnement (local, Railway.app ou Render.com).
        """
        # Configuration du logging
        self.logger = logging.getLogger('storage_manager')
        
        # Déterminer l'environnement
        self.is_railway = 'RAILWAY_STORAGE_PATH' in os.environ
        self.is_render = 'RENDER' in os.environ
        
        # Chemin de base pour le stockage
        if self.is_railway:
            # Sur Railway.app, utiliser le stockage persistant
            self.base_path = Path(os.environ.get('RAILWAY_STORAGE_PATH', '/data/storage'))
            self.logger.info(f"Environnement Railway.app détecté, utilisation du stockage persistant: {self.base_path}")
        elif self.is_render:
            # Sur Render.com, utiliser le disque persistant
            self.base_path = Path(os.environ.get('RENDER_DISK_PATH', '/opt/render/project/src/storage'))
            self.logger.info(f"Environnement Render.com détecté, utilisation du disque persistant: {self.base_path}")
        else:
            # En local, utiliser le répertoire de l'application
            self.base_path = Path(os.path.dirname(os.path.abspath(__file__)))
            self.logger.info(f"Environnement local détecté, utilisation du répertoire: {self.base_path}")
        
        # Définir les sous-répertoires
        self.upload_path = self.base_path / 'uploads'
        self.download_path = self.base_path / 'downloads'
        
        # Créer les répertoires s'ils n'existent pas
        self._ensure_directories()
    
    def _ensure_directories(self):
        """
        Assure que les répertoires de stockage existent.
        """
        self.logger.info("Vérification des répertoires de stockage")
        os.makedirs(self.upload_path, exist_ok=True)
        os.makedirs(self.download_path, exist_ok=True)
        self.logger.info(f"Répertoires créés/vérifiés: {self.upload_path}, {self.download_path}")
    
    def get_upload_path(self):
        """
        Retourne le chemin complet du répertoire de téléchargement.
        
        Returns:
            Path: Chemin du répertoire de téléchargement
        """
        return self.upload_path
    
    def get_download_path(self):
        """
        Retourne le chemin complet du répertoire de téléchargement.
        
        Returns:
            Path: Chemin du répertoire de téléchargement
        """
        return self.download_path
    
    def get_upload_file_path(self, filename):
        """
        Retourne le chemin complet pour un fichier téléchargé.
        
        Args:
            filename (str): Nom du fichier
            
        Returns:
            Path: Chemin complet du fichier
        """
        return self.upload_path / filename
    
    def get_download_file_path(self, filename):
        """
        Retourne le chemin complet pour un fichier généré.
        
        Args:
            filename (str): Nom du fichier
            
        Returns:
            Path: Chemin complet du fichier
        """
        return self.download_path / filename
    
    def cleanup_old_files(self, max_age_hours=24):
        """
        Nettoie les fichiers plus anciens que max_age_hours.
        
        Args:
            max_age_hours (int): Âge maximum des fichiers en heures
            
        Returns:
            int: Nombre de fichiers supprimés
        """
        import time
        from datetime import datetime, timedelta
        
        self.logger.info(f"Nettoyage des fichiers plus anciens que {max_age_hours} heures")
        
        # Calculer le timestamp limite
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cutoff_timestamp = cutoff_time.timestamp()
        
        # Compter les fichiers supprimés
        deleted_count = 0
        
        # Nettoyer les répertoires
        for directory in [self.upload_path, self.download_path]:
            for file_path in directory.glob('*'):
                if file_path.is_file():
                    # Vérifier l'âge du fichier
                    file_mtime = file_path.stat().st_mtime
                    if file_mtime < cutoff_timestamp:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                            self.logger.info(f"Fichier supprimé: {file_path}")
                        except Exception as e:
                            self.logger.error(f"Erreur lors de la suppression du fichier {file_path}: {str(e)}")
        
        self.logger.info(f"{deleted_count} fichiers supprimés")
        return deleted_count
    
    def is_render_environment(self):
        """
        Vérifie si l'application s'exécute sur Render.com.
        
        Returns:
            bool: True si sur Render.com, False sinon
        """
        return self.is_render
