import os
import uuid
import logging
from docx import Document
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session
from flask_session import Session
from werkzeug.utils import secure_filename
from cv_processor import CVProcessor
from storage_manager import StorageManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cv_analyzer_app')

# Configuration de l'application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'votre_cle_secrete_ici')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
app.config['SESSION_FILE_DIR'] = str(storage_manager.get_upload_path())
app.config['SESSION_FILE_THRESHOLD'] = 100
app.config['SESSION_FILE_MODE'] = 0o600

# Initialisation du gestionnaire de stockage
storage_manager = StorageManager()
logger.info(f"Gestionnaire de stockage initialisé. Environnement Render: {storage_manager.is_render_environment()}")

# Configuration des dossiers de stockage
UPLOAD_FOLDER = str(storage_manager.get_upload_path())
DOWNLOAD_FOLDER = str(storage_manager.get_download_path())

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Initialisation de Flask-Session
Session(app)

# Extensions autorisées
ALLOWED_EXTENSIONS = {'docx', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialisation du processeur de CV
cv_processor = CVProcessor(UPLOAD_FOLDER, DOWNLOAD_FOLDER)

# Nettoyage périodique des fichiers anciens
# Utilisation d'un hook d'initialisation compatible avec les versions récentes de Flask
@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Endpoint pour nettoyer les fichiers anciens (protégé par clé d'API)"""
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != os.environ.get('CLEANUP_API_KEY', 'secret_cleanup_key'):
        return jsonify({"error": "Non autorisé"}), 401
    
    try:
        deleted_count = storage_manager.cleanup_old_files(max_age_hours=24)
        logger.info(f"Nettoyage manuel: {deleted_count} fichiers supprimés")
        return jsonify({"success": True, "deleted_count": deleted_count})
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Fonction pour le nettoyage initial, appelée au démarrage
def cleanup_on_startup():
    """Nettoie les fichiers anciens au démarrage de l'application"""
    logger.info("Nettoyage initial des fichiers anciens")
    try:
        deleted_count = storage_manager.cleanup_old_files(max_age_hours=24)
        logger.info(f"Nettoyage initial: {deleted_count} fichiers supprimés")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage initial: {str(e)}")

# Exécuter le nettoyage initial
cleanup_on_startup()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    logger.info("Début du traitement d'une demande d'adaptation de CV")
    
    # Vérifier que la méthode est POST
    if request.method != 'POST':
        logger.warning(f"Méthode non autorisée: {request.method}")
        flash('Méthode non autorisée. Veuillez utiliser POST pour envoyer des fichiers', 'error')
        return jsonify({"error": "Method not allowed", "allowed_methods": ["POST"]}), 405
    
    # Vérifier si la requête contient un fichier
    if 'cv_file' not in request.files:
        logger.warning("Aucun fichier sélectionné dans la requête")
        flash('Aucun fichier sélectionné', 'error')
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['cv_file']
    
    # Si l'utilisateur n'a pas sélectionné de fichier
    if file.filename == '':
        logger.warning("Nom de fichier vide")
        flash('Aucun fichier sélectionné', 'error')
        return redirect(request.url)
    
    # Vérifier si le fichier est autorisé
    if not allowed_file(file.filename):
        logger.warning(f"Format de fichier non autorisé: {file.filename}")
        flash('Format de fichier non autorisé. Veuillez télécharger un fichier .docx ou .pdf', 'error')
        return redirect(request.url)
    
    # Récupérer la description du poste
    job_description = request.form.get('job_description', '')
    
    if not job_description:
        logger.warning("Description de poste vide")
        flash('Veuillez entrer une description de poste', 'error')
        return redirect(request.url)
    
    try:
        # Sécuriser le nom du fichier
        filename = secure_filename(file.filename)
        logger.info(f"Traitement du fichier: {filename}")
        
        # Générer un nom unique pour éviter les collisions
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Chemin complet du fichier
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Sauvegarder le fichier
        file.save(filepath)
        logger.info(f"Fichier sauvegardé: {filepath}")
        
        # Adapter le CV
        result = cv_processor.adapt_cv(filepath, job_description)
        
        # Stocker les statistiques dans la session pour affichage
        if isinstance(result, dict) and 'stats' in result:
            session['stats'] = result['stats']
            session['keywords'] = result.get('keywords', {})
        
        # Rediriger vers la page de téléchargement
        logger.info(f"CV adapté avec succès: {result['filename']}")
        return redirect(url_for('download_file', filename=result['filename']))
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier: {str(e)}")
        flash(f'Erreur lors du traitement du fichier: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/download/<filename>')
def download_file(filename):
    logger.info(f"Affichage de la page de téléchargement pour: {filename}")
    return render_template('download.html', filename=filename)

@app.route('/get_file/<filename>')
def get_file(filename):
    logger.info(f"Téléchargement du fichier: {filename}")
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint pour analyser une description de poste sans adapter de CV"""
    logger.info("Appel de l'API d'analyse de description de poste")
    
    if not request.is_json:
        logger.warning("Requête non JSON reçue")
        return jsonify({"error": "La requête doit être au format JSON"}), 400
    
    data = request.get_json()
    job_description = data.get('job_description', '')
    
    if not job_description:
        logger.warning("Description de poste vide dans la requête API")
        return jsonify({"error": "La description de poste est requise"}), 400
    
    try:
        # Analyser la description de poste
        analysis = cv_processor.analyze_job_description(job_description)
        logger.info("Analyse de la description de poste réussie")
        return jsonify({"success": True, "analysis": analysis})
    
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de la description de poste: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"Page non trouvée: {request.path}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Erreur serveur: {str(e)}")
    return render_template('500.html'), 500

@app.route('/stats')
def stats():
    """Page de statistiques sur l'utilisation de l'application"""
    logger.info("Affichage de la page de statistiques")
    # Dans une version plus complète, on pourrait stocker et afficher des statistiques d'utilisation
    return jsonify({
        "status": "ok",
        "uptime": "Service actif",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    logger.info("Démarrage de l'application CV Analyzer")
    app.run(host='0.0.0.0', debug=False)
