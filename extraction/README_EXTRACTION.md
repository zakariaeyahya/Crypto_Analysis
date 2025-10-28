# Extraction de Données Cryptomonnaies

## 📊 Sources de Données

Ce module permet l'extraction de données sur les cryptomonnaies depuis plusieurs sources.

### ✅ Reddit (Fonctionnel)
- **Source** : Subreddits cryptomonnaies (r/CryptoCurrency)
- **Type de données** : Posts, commentaires, métriques d'engagement
- **Format** : CSV
- **Localisation** : `data/bronze/reddit/`

### ⚠️ Twitter (Non Fonctionnel)
- **Statut** : API Twitter nécessite un accès payant (API v2)
- **Problème** : Erreur 401 Unauthorized - Credentials invalides
- **Solution Alternative** : Données de test disponibles
- **Localisation** : `data/bronze/twitter/`

## 🏗️ Architecture des Données (Medallion)

```
data/
├── bronze/              # Couche Bronze : Données brutes
│   ├── reddit/         # Données Reddit (CSV)
│   └── twitter/        # Données Twitter (CSV)
├── silver/             # Couche Silver : Données nettoyées (à venir)
│   ├── reddit/
│   └── twitter/
└── gold/               # Couche Gold : Données enrichies (à venir)
```

### Bronze Layer
- **Contenu** : Données brutes extraites des APIs
- **Format** : CSV
- **Pas de transformation** : Données telles quelles

### Silver Layer
- **Contenu** : Données nettoyées et validées (à implémenter)
- **Format** : CSV/Parquet
- **Transformations** : Nettoyage, déduplication

### Gold Layer
- **Contenu** : Données enrichies et agrégées (à implémenter)
- **Format** : Parquet optimisé
- **Usage** : Prêt pour visualisation et ML

## 🚀 Utilisation

### Extraction Reddit

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Lancer l'extraction
python extraction/services/reddit_extractor.py
```

**Configuration dans `.env`** :
```env
# Reddit API
CLIENT_ID=votre_client_id
CLIENT_SECRET=votre_client_secret
REDDIT_USERNAME=votre_username
REDDIT_SECRET=votre_password

# Configuration
REDDIT_SUBREDDIT=CryptoCurrency
MAX_POSTS=100
```

### Extraction Twitter (Non Fonctionnel)

```powershell
# Note: Nécessite des credentials API valides
python extraction/services/twitter_extractor.py
```

**Problème** : L'API Twitter nécessite un accès payant et les credentials fournis sont invalides (erreur 401).

**Solution Alternative** : Utiliser des données de test si disponibles.

## 📁 Structure des Fichiers Extraits

### Reddit
```
data/bronze/reddit/reddit_posts_YYYYMMDD_HHMMSS.csv
data/bronze/reddit/reddit_posts_YYYYMMDD_HHMMSS_summary.json
```

**Colonnes du CSV** :
- `submission_id` : ID du post
- `title` : Titre du post
- `text` : Contenu du post
- `body` : Contenu du commentaire
- `score` : Score du post
- `num_comments` : Nombre de commentaires
- `upvote_ratio` : Ratio de votes positifs
- `author` : Auteur
- `subreddit` : Subreddit
- `created_datetime` : Date de création
- `source` : Source des données

### Twitter
```
data/bronze/twitter/twitter_tweets_YYYYMMDD_HHMMSS.csv
data/bronze/twitter/twitter_tweets_YYYYMMDD_HHMMSS_summary.json
```

**Note** : Twitter extraction actuellement indisponible.

## 🛠️ Services Disponibles

### `reddit_extractor.py`
- ✅ Extraction de posts et commentaires Reddit
- ✅ Nettoyage automatique des données
- ✅ Sauvegarde CSV dans bronze/reddit
- ✅ Logs détaillés

### `twitter_extractor.py`
- ⚠️ Nécessite credentials API valides
- ⚠️ Actuellement non fonctionnel (401 Unauthorized)
- Format CSV dans bronze/twitter

## 📊 Statistiques d'Extraction

Les fichiers `_summary.json` contiennent :
- Nombre total de posts/tweets
- Date d'extraction
- Statistiques agrégées (likes, retweets, etc.)
- Métadonnées de fichier

## 🔧 Dépendances

```
tweepy          # Twitter API (si fonctionnel)
praw            # Reddit API
pandas          # Data processing
python-dotenv   # Configuration
```

## ⚠️ Limitations

1. **Twitter API** : Nécessite un abonnement payant pour l'accès à l'API v2
2. **Rate Limits** : 
   - Reddit : 60 requêtes/minute
   - Twitter : Limité par le plan d'abonnement
3. **Données** : Seulement les données récentes disponibles

## 📝 Logs

Toutes les opérations sont loguées dans :
- **Console** : Affichage en temps réel
- **Fichier** : `extraction.log`

## 🎯 Prochaines Étapes

1. ✅ Extraction Reddit opérationnelle
2. ⏳ Implémenter le traitement Silver layer
3. ⏳ Implémenter l'enrichissement Gold layer
4. ⏳ Fixer l'authentification Twitter ou trouver alternative
5. ⏳ Ajouter d'autres sources de données

## 👥 Contribution

Branche : `feature/zakariae-twitter-extraction`
Phase : Extraction (Bronze layer)

