# CV Analyzer

Application web responsive qui permet d'adapter un CV en format Word à une description de poste et de générer un CV optimisé pour cette offre d'emploi.

## Fonctionnalités

- Téléchargement de CV au format Word (.docx)
- Analyse intelligente des descriptions de poste
- Mise en évidence des compétences pertinentes dans le CV
- Génération d'un CV adapté téléchargeable
- Statistiques détaillées sur les correspondances
- Interface responsive adaptée à tous les appareils

## Démo

Une version de démonstration est disponible à l'adresse : [https://cv-analyzer.onrender.com](https://cv-analyzer.onrender.com)

## Installation locale

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Environnement virtuel (recommandé)

### Étapes d'installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/cv-analyzer.git
   cd cv-analyzer
   ```

2. Créez et activez un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Lancez l'application :
   ```bash
   python app.py
   ```

5. Accédez à l'application dans votre navigateur à l'adresse : [http://localhost:5000](http://localhost:5000)

## Déploiement sur Render.com

### Configuration requise

Pour déployer cette application sur Render.com, vous devez configurer un disque persistant pour le stockage des fichiers téléchargés et générés.

### Étapes de déploiement

1. Créez un compte sur [Render.com](https://render.com) si vous n'en avez pas déjà un.

2. Depuis le tableau de bord, cliquez sur "New" puis "Web Service".

3. Connectez votre dépôt GitHub ou GitLab contenant le code de l'application.

4. Configurez le service :
   - **Name** : cv-analyzer (ou un nom de votre choix)
   - **Environment** : Python
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app`

5. Dans l'onglet "Environment", ajoutez les variables d'environnement suivantes :
   - `SECRET_KEY` : Une clé secrète pour sécuriser votre application
   - `CLEANUP_API_KEY` : Une clé pour l'API de nettoyage des fichiers

6. Dans l'onglet "Disks", ajoutez un disque persistant :
   - **Name** : storage
   - **Mount Path** : `/opt/render/project/src/storage`
   - **Size** : 1 GB (ou plus selon vos besoins)

7. Cliquez sur "Create Web Service" pour déployer l'application.

## Structure du projet

```
cv-analyzer/
├── app.py                 # Application Flask principale
├── cv_processor.py        # Classe pour le traitement des CV
├── storage_manager.py     # Gestionnaire de stockage persistant
├── requirements.txt       # Dépendances du projet
├── static/                # Fichiers statiques (CSS, JS)
│   └── css/
│       └── style.css      # Styles de l'application
├── templates/             # Templates HTML
│   ├── index.html         # Page d'accueil
│   ├── download.html      # Page de téléchargement
│   ├── 404.html           # Page d'erreur 404
│   └── 500.html           # Page d'erreur 500
├── uploads/               # Dossier pour les CV téléchargés
└── downloads/             # Dossier pour les CV adaptés générés
```

## Technologies utilisées

- **Backend** : Flask (Python)
- **Traitement de documents** : python-docx, docx2txt
- **Frontend** : HTML, CSS, JavaScript
- **Déploiement** : Render.com avec stockage persistant

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
