# Crypto Analysis - Extraction de Tweets

Projet d'extraction et d'analyse de tweets sur les cryptomonnaies.

## 🚀 Démarrage Rapide

### 1. Activation du venv
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Installation des dépendances
```powershell
pip install -r requirements.txt
```

### 3. Configuration
Créez un fichier `.env` avec vos identifiants Twitter API (voir `.env.example`)

### 4. Extraction
```powershell
python extraction/services/twitter_extractor.py
```

## 📁 Structure

- `extraction/` : Code d'extraction de tweets
- `data/bronze/` : Données brutes extraites
- `data/silver/` : Données nettoyées (à venir)
- `data/gold/` : Données enrichies (à venir)

## 📖 Documentation

Consultez `README_TWITTER_EXTRACTION.md` pour plus de détails.

## 👥 Contribution

Branche: `feature/zakariae-twitter-extraction`