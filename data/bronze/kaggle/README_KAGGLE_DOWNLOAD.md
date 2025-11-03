# 📥 Instructions pour télécharger le dataset Kaggle

## 🎯 Objectif

Ce document explique comment exécuter le script `extraction/services/kaggle_downloader.py` pour télécharger le dataset Kaggle des tweets Bitcoin avec sentiment.

## 🚀 Exécution du script

### Prérequis

1. **Activer l'environnement virtuel** :
```powershell
.\venv\Scripts\Activate.ps1
```

2. **Installer la dépendance kagglehub** (si nécessaire) :
```powershell
pip install kagglehub[pandas-datasets]
```

### Exécution

Pour télécharger le dataset Kaggle, exécutez simplement :

```powershell
python extraction/services/kaggle_downloader.py
```

## 📊 Résultats

Après l'exécution, les fichiers suivants seront créés dans `data/bronze/kaggle/` :

### Fichiers générés

1. **Fichier CSV principal** :
   - Nom : `bitcoin_tweets_YYYYMMDD_HHMMSS.csv`
   - Contenu : Dataset complet avec les tweets Bitcoin
   - Taille : ~3 GB (19344048 records)
   - Colonnes : `Date`, `text`, `Sentiment`

2. **Fichier de résumé** :
   - Nom : `bitcoin_tweets_YYYYMMDD_HHMMSS_summary.json`
   - Contenu : Métadonnées et statistiques du dataset
   - Exemple :
   ```json
   {
     "total_records": 19344048,
     "columns": ["Date", "text", "Sentiment"],
     "dataset_name": "gauravduttakiit/bitcoin-tweets-16m-tweets-with-sentiment-tagged",
     "download_date": "2025-11-03T22:10:00.136723",
     "file_location": "data\\bronze\\kaggle\\bitcoin_tweets_20251103_220752.csv",
     "file_size_mb": 3109.45
   }
   ```

3. **Fichier de checkpoint** :
   - Nom : `kaggle_downloads_checkpoint.json`
   - Contenu : Historique des téléchargements
   - Utilisation : Empêche le re-téléchargement si le dataset existe déjà

## ⚙️ Fonctionnement

### Système de checkpoint

Le script utilise un système de checkpoint pour éviter les téléchargements redondants :

- ✅ **Si le fichier existe déjà** : Le script détecte automatiquement le fichier existant et le charge sans re-téléchargement
- ✅ **Si le fichier n'existe pas** : Le script télécharge le dataset depuis Kaggle et le sauvegarde

### Exemple de sortie

**Premier téléchargement** :
```
2025-11-03 22:07:52 - INFO - [OK] Dataset downloaded to: /path/to/kaggle/dataset
2025-11-03 22:07:53 - INFO - [INFO] Found 1 CSV file(s): ['Bitcoin_tweets.csv']
2025-11-03 22:10:25 - INFO - [OK] Dataset loaded successfully in 152.45 seconds
2025-11-03 22:10:25 - INFO -   Records: 19344048
2025-11-03 22:10:25 - INFO - [OK] Saved 19344048 records to data/bronze/kaggle/bitcoin_tweets_20251103_221025.csv
```

**Réexécution (fichier existant)** :
```
2025-11-03 22:15:00 - INFO - [INFO] Dataset already downloaded: data/bronze/kaggle/bitcoin_tweets_20251103_221025.csv
2025-11-03 22:15:00 - INFO - [INFO] Using existing downloaded dataset
2025-11-03 22:15:05 - INFO - [OK] Loaded 19344048 records from existing file
```

## 🔄 Réexécution

Pour réexécuter le script et obtenir le fichier CSV :

1. Ouvrir PowerShell dans le répertoire racine du projet
2. Activer l'environnement virtuel
3. Exécuter : `python extraction/services/kaggle_downloader.py`

Le script détectera automatiquement si le fichier existe déjà et chargera le fichier existant au lieu de le re-télécharger.

## 📝 Notes importantes

- ⚠️ **Taille du fichier** : Le fichier CSV est volumineux (~3 GB), assurez-vous d'avoir suffisamment d'espace disque
- ⚠️ **Git** : Les fichiers CSV et JSON sont ignorés par Git (voir `.gitignore`) pour éviter de pousser des fichiers volumineux
- ✅ **Idempotent** : Le script peut être exécuté plusieurs fois sans risque de duplication
- ✅ **Checkpoint** : Le fichier `kaggle_downloads_checkpoint.json` garde l'historique des téléchargements

## 🐛 Dépannage

### Erreur : "kagglehub library not installed"
```powershell
pip install kagglehub[pandas-datasets]
```

### Erreur : "No CSV files found"
- Vérifiez que le dataset Kaggle contient des fichiers CSV
- Vérifiez votre connexion internet

### Le script télécharge toujours même si le fichier existe
- Vérifiez que le fichier `kaggle_downloads_checkpoint.json` existe
- Vérifiez que le chemin dans le checkpoint correspond au fichier réel

## 📚 Documentation complète

Pour plus de détails, consultez :
- `extraction/README_EXTRACTION.md` - Documentation complète du module d'extraction
- `extraction/services/kaggle_downloader.py` - Code source du script

