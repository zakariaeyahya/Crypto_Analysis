# Configuration Auto-Push GitHub depuis Railway

Guide pour configurer le push automatique des données extraites vers GitHub depuis Railway.

## Objectif

Après chaque extraction de données sur Railway :
1. Les données CSV sont générées dans `data/bronze/reddit/`
2. Le DAG commit et push automatiquement sur GitHub
3. Vous faites `git pull` en local pour récupérer les données
4. Les autres développeurs font aussi `git pull` pour accéder aux données

---

## Étape 1 : Créer un Personal Access Token GitHub

### 1.1 Accéder aux paramètres GitHub

1. Allez sur https://github.com/settings/tokens
2. Cliquez sur **"Generate new token"** → **"Generate new token (classic)"**

### 1.2 Configurer le token

**Name** : `Railway Airflow Auto-Push`

**Expiration** : `No expiration` (ou 1 an selon votre politique de sécurité)

**Scopes** : Cochez uniquement :
- ✅ `repo` (Full control of private repositories)
  - Cela inclut `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, `security_events`

### 1.3 Générer et copier le token

1. Cliquez sur **"Generate token"**
2. **COPIEZ LE TOKEN IMMÉDIATEMENT** : `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
3. ⚠️ Vous ne pourrez plus le voir après avoir quitté la page

---

## Étape 2 : Configurer les variables d'environnement Railway

### 2.1 Accéder à votre service Railway

1. Allez sur https://railway.app
2. Ouvrez votre projet : https://railway.com/project/cb92fccf-4617-4a32-b044-fe6e191c1406
3. Cliquez sur votre service `cryptoanalysis-production`
4. Onglet **"Variables"**

### 2.2 Ajouter les variables suivantes

Cliquez sur **"New Variable"** et ajoutez une par une :

```bash
# Token GitHub (celui que vous venez de créer)
GITHUB_TOKEN=ghp_votre_token_ici

# Nom du repository (format: username/repo)
GITHUB_REPO=zakariaeyahya/Crypto_Analysis

# Branche sur laquelle pusher
GITHUB_BRANCH=main

# Configuration Git (pour les commits)
GIT_USER_NAME=zakariaeyahya
GIT_USER_EMAIL=votre.email@example.com

# Enable auto-push (pour activer/désactiver facilement)
ENABLE_GITHUB_PUSH=true
```

### 2.3 Sauvegarder

Cliquez sur **"Save"** - Railway va redéployer automatiquement.

---

## Étape 3 : Installer Git dans le conteneur Docker

### 3.1 Modifier le Dockerfile

Le Dockerfile doit installer Git pour pouvoir faire des commits.

**Fichier** : `docker/Dockerfile.airflow`

**Modification** : Ajouter `git` dans l'installation des dépendances système.

**Avant** :
```dockerfile
RUN apt-get update && \
    apt-get install -y gcc curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

**Après** :
```dockerfile
RUN apt-get update && \
    apt-get install -y gcc curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

---

## Étape 4 : Créer le script de push GitHub

### 4.1 Créer un nouveau fichier

**Fichier** : `scripts/push_to_github.py`

```python
#!/usr/bin/env python3
"""
Script to push extracted data to GitHub automatically
"""
import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_command(cmd, cwd=None):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd}")
        logger.error(f"Error: {e.stderr}")
        raise


def setup_git_config():
    """Configure Git user"""
    git_user = os.getenv('GIT_USER_NAME', 'Airflow Bot')
    git_email = os.getenv('GIT_USER_EMAIL', 'airflow@railway.app')

    run_command(f'git config --global user.name "{git_user}"')
    run_command(f'git config --global user.email "{git_email}"')
    logger.info(f"Git configured: {git_user} <{git_email}>")


def push_data_to_github():
    """Push extracted data to GitHub"""

    # Check if auto-push is enabled
    if os.getenv('ENABLE_GITHUB_PUSH', 'false').lower() != 'true':
        logger.info("GitHub auto-push is disabled (ENABLE_GITHUB_PUSH != true)")
        return

    # Get environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    github_repo = os.getenv('GITHUB_REPO')
    github_branch = os.getenv('GITHUB_BRANCH', 'main')

    if not github_token or not github_repo:
        logger.error("Missing GITHUB_TOKEN or GITHUB_REPO environment variables")
        raise ValueError("GitHub credentials not configured")

    # Working directory
    repo_path = Path('/opt/airflow')

    logger.info("=" * 60)
    logger.info("Starting GitHub auto-push")
    logger.info("=" * 60)

    # Setup Git config
    setup_git_config()

    # Check if we're in a git repository
    if not (repo_path / '.git').exists():
        logger.info("Initializing Git repository...")
        run_command('git init', cwd=repo_path)

        # Add remote with token authentication
        remote_url = f"https://{github_token}@github.com/{github_repo}.git"
        run_command(f'git remote add origin {remote_url}', cwd=repo_path)
        logger.info(f"Added remote: {github_repo}")

    # Fetch latest changes
    logger.info(f"Fetching from {github_branch}...")
    try:
        run_command(f'git fetch origin {github_branch}', cwd=repo_path)
        run_command(f'git checkout {github_branch}', cwd=repo_path)
    except subprocess.CalledProcessError:
        logger.warning(f"Branch {github_branch} doesn't exist, creating it")
        run_command(f'git checkout -b {github_branch}', cwd=repo_path)

    # Check if there are changes in data/ directory
    run_command('git add data/', cwd=repo_path)

    try:
        status = run_command('git status --porcelain', cwd=repo_path)
        if not status:
            logger.info("No changes to commit")
            return
    except subprocess.CalledProcessError:
        logger.warning("Could not check git status")

    # Create commit message
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    commit_message = f"""Data extraction update - {timestamp}

Automated data extraction from Railway Airflow
- Reddit cryptocurrency posts and comments
- Date: {datetime.now().strftime('%Y-%m-%d')}

🤖 Generated by Airflow on Railway
"""

    # Commit changes
    logger.info("Committing changes...")
    run_command(f'git commit -m "{commit_message}"', cwd=repo_path)

    # Push to GitHub
    logger.info(f"Pushing to {github_repo}/{github_branch}...")
    remote_url = f"https://{github_token}@github.com/{github_repo}.git"
    run_command(f'git push {remote_url} {github_branch}', cwd=repo_path)

    logger.info("=" * 60)
    logger.info("✅ Data successfully pushed to GitHub!")
    logger.info(f"Repository: https://github.com/{github_repo}")
    logger.info(f"Branch: {github_branch}")
    logger.info("=" * 60)


if __name__ == '__main__':
    try:
        push_data_to_github()
    except Exception as e:
        logger.error(f"Failed to push to GitHub: {e}")
        raise
```

---

## Étape 5 : Modifier le DAG Reddit

### 5.1 Ajouter la tâche de push GitHub

**Fichier** : `airflow/dags/reddit_extraction_dag.py`

**Ajouter après les imports** :
```python
import sys
sys.path.insert(0, '/opt/airflow/scripts')
from push_to_github import push_data_to_github
```

**Ajouter la fonction** :
```python
def push_data_to_git(**context):
    """Push extracted data to GitHub"""
    logger.info("Pushing data to GitHub...")
    push_data_to_github()
    logger.info("Data pushed successfully")
```

**Modifier le DAG (avant la fermeture du `with DAG`)** :
```python
with DAG(
    dag_id=reddit_config['dag_id'],
    description=reddit_config['description'],
    schedule_interval=reddit_config['schedule_interval'],
    start_date=datetime.strptime(reddit_config['start_date'], '%Y-%m-%d'),
    catchup=reddit_config['catchup'],
    max_active_runs=reddit_config['max_active_runs'],
    default_args=default_args,
    tags=['reddit', 'crypto', 'extraction']
) as dag:

    extract_task = PythonOperator(
        task_id=reddit_config['task_id'],
        python_callable=extract_reddit_data,
        provide_context=True
    )

    # NOUVELLE TÂCHE : Push to GitHub
    push_task = PythonOperator(
        task_id='push_to_github',
        python_callable=push_data_to_git,
        provide_context=True
    )

    # Définir l'ordre d'exécution
    extract_task >> push_task
```

---

## Étape 6 : Copier les fichiers nécessaires dans le Docker

### 6.1 Modifier le Dockerfile

**Fichier** : `docker/Dockerfile.airflow`

**Ajouter après la copie du script de démarrage** :
```dockerfile
# Copy GitHub push script
COPY --chown=airflow:root scripts/push_to_github.py /opt/airflow/scripts/push_to_github.py
```

---

## Étape 7 : Déployer sur Railway

### 7.1 Commit et push les changements

```bash
git add docker/Dockerfile.airflow
git add scripts/push_to_github.py
git add airflow/dags/reddit_extraction_dag.py
git commit -m "feat: add GitHub auto-push for extracted data"
git push origin main
```

### 7.2 Vérifier le déploiement Railway

1. Railway va détecter automatiquement les changements
2. Un nouveau build va commencer
3. Attendez que le build se termine (environ 2-3 minutes)
4. Vérifiez les logs pour voir si le démarrage est OK

---

## Étape 8 : Tester le workflow

### 8.1 Déclencher le DAG manuellement

1. Allez sur https://cryptoanalysis-production.up.railway.app
2. Connectez-vous (airflow/airflow)
3. Cliquez sur le DAG `reddit_crypto_extraction`
4. Cliquez sur le bouton "Play" ▶️ (Trigger DAG)

### 8.2 Vérifier l'exécution

1. Suivez l'exécution dans l'interface Airflow
2. Vérifiez que les 2 tâches se complètent :
   - ✅ `extract_reddit_posts`
   - ✅ `push_to_github`

### 8.3 Vérifier sur GitHub

1. Allez sur https://github.com/zakariaeyahya/Crypto_Analysis/commits/main
2. Vous devriez voir un nouveau commit avec le message :
   ```
   Data extraction update - 2025-11-15 XX:XX:XX UTC
   ```
3. Vérifiez que les fichiers sont présents dans `data/bronze/reddit/`

### 8.4 Récupérer les données en local

```bash
cd /path/to/Crypto_Analysis
git pull origin main
```

Les nouvelles données devraient apparaître dans votre dossier `data/`.

---

## Dépannage

### Erreur : "GitHub token invalid"

**Cause** : Le token GitHub est incorrect ou expiré

**Solution** :
1. Vérifiez que le token commence par `ghp_`
2. Créez un nouveau token sur GitHub
3. Mettez à jour `GITHUB_TOKEN` dans Railway

### Erreur : "Permission denied"

**Cause** : Le token n'a pas les permissions `repo`

**Solution** :
1. Recréez le token avec le scope `repo` complet
2. Mettez à jour dans Railway

### Pas de commit créé

**Cause** : Aucune donnée extraite ou données déjà commitées

**Solution** :
1. Vérifiez les logs de la tâche `extract_reddit_posts`
2. Vérifiez qu'il y a bien des données extraites
3. Le script ne commit que s'il y a des changements dans `data/`

### Conflit Git

**Cause** : Le dossier `/opt/airflow` contient déjà un repository Git

**Solution** :
Le script gère automatiquement ce cas en faisant un `fetch` avant de commit

### Auto-push désactivé

**Vérification** :
```bash
# Dans les logs Railway, vous devriez voir :
# "GitHub auto-push is disabled (ENABLE_GITHUB_PUSH != true)"
```

**Solution** :
Assurez-vous que `ENABLE_GITHUB_PUSH=true` dans Railway

---

## Workflow complet

```
1. Railway Airflow exécute le DAG
   ↓
2. Tâche "extract_reddit_posts"
   - Extraction des données Reddit
   - Sauvegarde dans data/bronze/reddit/year=YYYY/month=MM/day=DD/
   ↓
3. Tâche "push_to_github"
   - git add data/
   - git commit -m "Data extraction update..."
   - git push origin main
   ↓
4. GitHub repository mis à jour
   ↓
5. Vous (en local): git pull origin main
   ↓
6. Données disponibles localement dans data/
```

---

## Désactiver l'auto-push temporairement

Si vous voulez désactiver l'auto-push sans modifier le code :

**Dans Railway** :
```
ENABLE_GITHUB_PUSH=false
```

Le DAG continuera à extraire les données mais ne les pushera pas.

---

## Sécurité

### ⚠️ Ne jamais commit le token GitHub

Le token est stocké uniquement dans les variables d'environnement Railway.
Ne l'ajoutez jamais dans le code ou dans `.env`.

### Rotation du token

Il est recommandé de régénérer le token tous les 6-12 mois pour la sécurité.

---

## Prochaines étapes

Une fois que l'auto-push fonctionne :

1. **Automatiser l'extraction** : Configurez un `schedule_interval` dans le DAG
2. **Ajouter l'EDA** : Créez un nouveau DAG pour l'analyse exploratoire
3. **Notifications** : Ajoutez des notifications Slack/Email quand les données sont pushées
4. **Tests** : Ajoutez des tests de qualité des données avant le push
