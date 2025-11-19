# Guide de Déploiement Airflow - Solutions Gratuites

## 🎯 Vue d'ensemble

Ce guide explique comment déployer votre projet Airflow sur des plateformes cloud gratuites.

## ⚠️ Limitations importantes

**Airflow nécessite 3 services qui doivent tourner 24/7 :**
- PostgreSQL (base de données)
- Webserver (interface web)
- Scheduler (exécution des DAGs)

**Les plans gratuits ont des limitations :**
- Services qui peuvent s'arrêter après inactivité
- Quotas de ressources limités
- Persistance des données limitée

---

## 🚂 Option 1 : Railway.app (RECOMMANDÉ)

### Avantages
- ✅ 500$ de crédit gratuit/mois
- ✅ Support Docker
- ✅ Pas de sleep automatique (si service actif)
- ✅ Facile à configurer

### Étapes de déploiement

#### 1. Créer un compte Railway
- Aller sur https://railway.app
- Se connecter avec GitHub

#### 2. Créer un nouveau projet
- Cliquer sur "New Project"
- Sélectionner "Deploy from GitHub repo"
- Choisir votre repository `Crypto_Analysis`

#### 3. Configurer les services

**Service 1 : PostgreSQL**
- Ajouter un service "PostgreSQL"
- Railway créera automatiquement une base de données
- Noter les variables d'environnement (DATABASE_URL, etc.)

**Service 2 : Airflow Webserver + Scheduler**
- Ajouter un service "Docker"
- Configurer :
  - Dockerfile: `docker/Dockerfile.airflow`
  - Command: `webserver` (pour webserver) OU créer un script qui lance les deux

**Service 3 : Scheduler (optionnel, peut être combiné)**
- Vous pouvez lancer webserver et scheduler dans le même conteneur avec un script

#### 4. Variables d'environnement
Dans Railway, ajouter toutes les variables de `.env.airflow` :
```
AIRFLOW_UID=50000
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__WEBSERVER__SECRET_KEY=<votre_clé>
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=<URL_de_railway_postgres>
CLIENT_ID=<reddit_client_id>
CLIENT_SECRET=<reddit_secret>
REDDIT_USERNAME=<username>
REDDIT_SECRET=<password>
```

#### 5. Volumes persistants
- Configurer un volume pour `data/` (données extraites)
- Configurer un volume pour `airflow/logs/` (logs Airflow)

### Script de démarrage combiné (webserver + scheduler)

Créer `scripts/start_airflow_combined.sh` :
```bash
#!/bin/bash
# Start both webserver and scheduler in one container

# Start scheduler in background
airflow scheduler &

# Start webserver in foreground
exec airflow webserver
```

---

## 🎨 Option 2 : Render

### Avantages
- ✅ Plan gratuit disponible
- ✅ Support Docker
- ✅ Services persistants

### Limitations
- ⚠️ Services gratuits peuvent s'arrêter après inactivité
- ⚠️ Besoin de "ping" régulier pour maintenir actif

### Étapes de déploiement

1. Créer un compte sur https://render.com
2. Créer un nouveau "Web Service"
3. Connecter votre repository GitHub
4. Configurer :
   - Environment: Docker
   - Dockerfile Path: `docker/Dockerfile.airflow`
   - Start Command: `webserver`

5. Ajouter les variables d'environnement (comme Railway)

6. **Important** : Pour maintenir le service actif, ajouter un healthcheck :
   - Render vérifiera automatiquement `/health`
   - Le scheduler doit tourner en arrière-plan

---

## ☁️ Option 3 : Google Cloud Run (NON RECOMMANDÉ)

**Pourquoi pas adapté :**
- Cloud Run est serverless (s'arrête après chaque requête)
- Le scheduler Airflow doit tourner en continu
- Ne peut pas maintenir un processus long

**Alternative** : Utiliser Google Compute Engine (VPS) avec le plan gratuit (300$ de crédit/mois)

---

## 🔧 Configuration adaptée pour cloud

### Modifier docker-compose pour Railway/Render

Ces plateformes ne supportent pas directement docker-compose. Options :

#### Option A : Script de démarrage combiné
Créer un script qui lance webserver et scheduler ensemble.

#### Option B : Services séparés
Déployer 3 services séparés (un pour postgres, un pour webserver, un pour scheduler).

---

## 📊 Comparaison des solutions

| Plateforme | Gratuit | 24/7 | Docker | Difficulté | Recommandation |
|------------|---------|------|--------|------------|----------------|
| **Railway** | ✅ 500$/mois | ✅ Oui | ✅ Oui | ⭐⭐ Facile | ⭐⭐⭐⭐⭐ |
| **Render** | ✅ Oui | ⚠️ Avec ping | ✅ Oui | ⭐⭐⭐ Moyen | ⭐⭐⭐ |
| **Heroku** | ✅ Limité | ❌ Sleep | ✅ Oui | ⭐⭐ Facile | ❌ Non |
| **Cloud Run** | ✅ Quota | ❌ Serverless | ✅ Oui | ⭐⭐⭐ Difficile | ❌ Non |

---

## 🎯 Recommandation finale

**Pour un déploiement gratuit et fiable :**

1. **Railway.app** (meilleur choix)
   - Facile à configurer
   - Crédit gratuit généreux
   - Services stables

2. **Alternative** : VPS gratuit (Oracle Cloud, AWS Free Tier)
   - Plus de contrôle
   - Nécessite plus de configuration
   - Ressources limitées mais suffisantes

---

## 📝 Notes importantes

1. **Persistance des données** : Configurez des volumes pour sauvegarder :
   - `data/bronze/` (données extraites)
   - `airflow/logs/` (logs)
   - Base de données PostgreSQL

2. **Secrets** : Ne jamais commiter `.env.airflow` (déjà dans `.gitignore`)

3. **Monitoring** : Vérifier régulièrement que les services tournent

4. **Backup** : Sauvegarder régulièrement les données importantes

---

## 🚀 Prochaines étapes

1. Choisir une plateforme (Railway recommandé)
2. Suivre les étapes de déploiement
3. Configurer les variables d'environnement
4. Tester le déploiement
5. Vérifier que les DAGs s'exécutent automatiquement

