# Documentation Pipeline de Donnees - CryptoVibe

## 1. Vue d'Ensemble

Le pipeline de donnees de CryptoVibe suit l'**architecture Medallion** (Bronze/Silver/Gold), un pattern de data engineering qui organise les donnees en couches de qualite croissante.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ARCHITECTURE MEDALLION                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   SOURCES              BRONZE            SILVER              GOLD            │
│                                                                              │
│  ┌─────────┐      ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │ Reddit  │─────▶│ Posts bruts  │──▶│ Posts        │──▶│ Sentiment    │    │
│  │ (PRAW)  │      │ JSON         │   │ nettoyes     │   │ Timeseries   │    │
│  └─────────┘      └──────────────┘   │ + NER        │   └──────────────┘    │
│                                      │ + Sentiment  │                        │
│  ┌─────────┐      ┌──────────────┐   └──────────────┘   ┌──────────────┐    │
│  │ Kaggle  │─────▶│ Tweets bruts │                      │ Correlations │    │
│  │ Bitcoin │      │ CSV          │──────────────────────▶│ JSON         │    │
│  │ Tweets  │      └──────────────┘                      └──────────────┘    │
│  └─────────┘                                                                 │
│                                      ┌──────────────┐   ┌──────────────┐    │
│  ┌─────────┐      ┌──────────────┐   │ Posts        │   │ Lag Analysis │    │
│  │ Yahoo   │─────▶│ Prix OHLC    │──▶│ enrichis     │──▶│ JSON         │    │
│  │ Finance │      │ CSV          │   │ + Prix       │   └──────────────┘    │
│  └─────────┘      └──────────────┘   └──────────────┘                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 2. Sources de Donnees

### 2.1 Reddit (PRAW)

**Module**: `extraction/`

| Parametre | Valeur |
|-----------|--------|
| Subreddit | r/CryptoCurrency |
| API | PRAW (Python Reddit API Wrapper) |
| Contenu | Posts + Commentaires |
| Periode | 30 derniers jours |

**Mecanismes**:
- Checkpoint pour eviter les doublons
- Retry automatique avec backoff exponentiel
- Rate limiting respecte

### 2.2 Kaggle - Bitcoin Tweets 16M

**Module**: `Finetuning/`

| Parametre | Valeur |
|-----------|--------|
| Dataset | Bitcoin Tweets 16M |
| Volume | 397 516 tweets (utilises) |
| Classes | Positive / Negative |
| Usage | Fine-tuning RoBERTa |

**Repartition**:
- 70% entrainement
- 15% validation
- 15% test (49 690 tweets)

### 2.3 Yahoo Finance (yfinance)

**Module**: `fetch_crypto_data/`

| Parametre | Valeur |
|-----------|--------|
| Cryptos | BTC-USD, ETH-USD, SOL-USD |
| Format | OHLC (Open, High, Low, Close) |
| Historique | Depuis 2014 |
| API | yfinance (gratuit, sans cle) |

**Commande**:
```bash
python fetch_crypto_data/fetch_crypto_data_yfinance.py
```

## 3. Couche Bronze - Donnees Brutes

### 3.1 Structure des Fichiers

```
data/bronze/
├── BTC/
│   └── historical_prices.csv
├── ETH/
│   └── historical_prices.csv
└── SOL/
    └── historical_prices.csv
```

### 3.2 Schema Prix (CSV)

| Colonne | Type | Description |
|---------|------|-------------|
| `date` | string | Date YYYY-MM-DD (UTC) |
| `crypto` | string | Symbole (BTC, ETH, SOL) |
| `price_open` | float | Prix d'ouverture USD |
| `price_close` | float | Prix de cloture USD |
| `volume` | float | Volume journalier USD |

### 3.3 Exemple

```csv
date,crypto,price_open,price_close,volume
2024-01-15,BTC,42500.0,43200.0,28500000000.0
2024-01-16,BTC,43200.0,42800.0,25600000000.0
```

## 4. Couche Silver - Donnees Nettoyees et Enrichies

### 4.1 Pipeline de Nettoyage

**Module**: `data_cleaning/`

**Statistiques**:
| Metrique | Valeur |
|----------|--------|
| Lignes initiales | 28 731 |
| Lignes finales | 27 138 |
| Lignes supprimees | 1 593 (5.54%) |
| Posts | 2 225 |
| Commentaires | 24 913 |
| Auteurs uniques | 12 802 |

**Criteres de suppression**:
| Critere | Lignes supprimees |
|---------|-------------------|
| Trop court (<10 car.) | 1 158 |
| Comptes bot | 334 |
| Court apres nettoyage | 101 |
| Dates invalides | 0 |
| Doublons | 0 |

### 4.2 Enrichissement des Entites (NER)

**Module**: `analysis/entity_extraction.py`

**Entites detectees**:
- Cryptomonnaies (BTC, ETH, SOL + variantes)
- Exchanges (Binance, Coinbase, Kraken...)
- Influenceurs (Elon Musk, Vitalik, CZ...)
- Hashtags et mentions
- Evenements (hack, regulation, pump, crash)

**Sortie**: `data/silver/enriched_data/enriched_data.json`

### 4.3 Jointure avec les Prix

**Module**: `analysis/data_price.py`

**Calcul de variation**:
```python
price_change = (close - open) / open
```

**Sortie**: `data/silver/enriched_data/crypto_sent_enriched_price.json`

### 4.4 Schema Silver (JSON)

```json
{
  "unified_id": "reddit_abc123",
  "text_content": "Bitcoin looking bullish today!",
  "created_date": "2024-01-15",
  "author": "crypto_trader",
  "source_platform": "reddit",
  "sentiment": "positive",
  "sentiment_score": 0.75,
  "entities": {
    "cryptos": ["BTC"],
    "exchanges": [],
    "influencers": []
  },
  "price_change": 0.0165
}
```

## 5. Couche Gold - Donnees Analysees

### 5.1 Structure des Fichiers

```
data/gold/
├── sentiment_timeseries.json      # Series temporelles sentiment
├── sentiment_price_correlation.json # Correlations Pearson
└── lag_analysis.json              # Analyse de decalage
```

### 5.2 Agregation Temporelle

**Module**: `analysis/time_serie_agregation.py`

**Metriques calculees par jour et par crypto**:
- Sentiment moyen
- Ecart-type
- Nombre de posts positifs/negatifs/neutres
- Moyenne mobile 7 jours
- Moyenne mobile 30 jours

**Sortie**: `data/gold/sentiment_timeseries.json`

```json
{
  "date": "2024-01-15",
  "crypto": "BTC",
  "sentiment_mean": 0.12,
  "sentiment_std": 0.35,
  "positive_count": 145,
  "negative_count": 78,
  "neutral_count": 52,
  "ma_7d": 0.15,
  "ma_30d": 0.10
}
```

### 5.3 Analyse de Correlation

**Module**: `analysis/correlation.py`

**Methode**: Correlation de Pearson entre sentiment quotidien et variation de prix.

**Sortie**: `data/gold/sentiment_price_correlation.json`

```json
{
  "crypto": "BTC",
  "correlation": -0.0795,
  "p_value": 0.0021,
  "n_observations": 1489,
  "interpretation": "negligible"
}
```

### 5.4 Analyse de Lag

**Module**: `analysis/lag_analysis.py`

**Tests effectues**:
- Correlation de Pearson
- Correlation de Spearman
- Test de causalite de Granger

**Echelles temporelles**:
- Journalier: sentiment(t) → prix(t+1)
- Hebdomadaire
- Mensuel

**Sortie**: `data/gold/lag_analysis.json`

## 6. Orchestration Airflow

### 6.1 DAG Principal

```
┌─────────────────────────────────────────────────────────────────┐
│                        AIRFLOW DAG                               │
│                    (Toutes les 6 heures)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   [Start] ──▶ [Scraping] ──▶ [Cleaning] ──▶ [NER] ──▶           │
│                                                                  │
│              ──▶ [Sentiment] ──▶ [Aggregation] ──▶ [End]        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Taches

| Tache | Description | Frequence |
|-------|-------------|-----------|
| `scrape_reddit` | Extraction posts Reddit | 6h |
| `fetch_prices` | Recuperation prix Yahoo | 6h |
| `clean_data` | Nettoyage et validation | 6h |
| `extract_entities` | NER (cryptos, exchanges) | 6h |
| `analyze_sentiment` | Classification RoBERTa | 6h |
| `aggregate_timeseries` | Agregation Gold | 6h |
| `compute_correlation` | Calcul correlations | 6h |

### 6.3 Performance

| Metrique | Valeur |
|----------|--------|
| Temps d'execution moyen | 25 minutes |
| Taux de succes | 95% |
| Volume traite | 27 138 entrees |

## 7. Flux de Donnees Complet

```
1. COLLECTE (Bronze)
   ├── Reddit PRAW ──────────▶ posts_raw.json
   ├── Kaggle Dataset ───────▶ tweets_raw.csv
   └── Yahoo Finance ────────▶ historical_prices.csv

2. NETTOYAGE (Bronze → Silver)
   ├── Suppression bots, spam, doublons
   ├── Normalisation dates
   └── Validation schema

3. ENRICHISSEMENT (Silver)
   ├── Extraction entites (NER)
   ├── Analyse sentiment (RoBERTa 70.1%)
   └── Jointure avec prix

4. AGREGATION (Silver → Gold)
   ├── Time series sentiment
   ├── Correlations Pearson
   └── Analyse lag

5. EXPOSITION (Gold → API)
   ├── FastAPI endpoints
   ├── Indexation Pinecone (RAG)
   └── Dashboard React
```

## 8. Commandes Utiles

### Collecte des Prix
```bash
python fetch_crypto_data/fetch_crypto_data_yfinance.py
```

### Nettoyage des Donnees
```bash
python data_cleaning/clean_data.py
```

### Enrichissement NER
```bash
python analysis/entity_extraction.py
```

### Agregation Sentiment
```bash
python analysis/time_serie_agregation.py
```

### Correlation
```bash
python analysis/correlation.py
```

### Analyse Lag
```bash
python analysis/lag_analysis.py
```

### Indexation Pinecone (RAG)
```bash
cd backend
python scripts/index_documents.py --clear
```

## 9. Fichiers de Donnees

### 9.1 Mapping Fichiers → Endpoints API

| Fichier | Endpoint | Description |
|---------|----------|-------------|
| `bronze/{symbol}/historical_prices.csv` | `/api/cryptos/*` | Prix historiques |
| `silver/enriched_data/crypto_sent_enriched_price.json` | `/api/events` | Posts enrichis |
| `gold/sentiment_timeseries.json` | `/api/sentiment/*` | Sentiment quotidien |
| `gold/sentiment_price_correlation.json` | `/api/analysis/*/correlation` | Correlations |
| `gold/lag_analysis.json` | `/api/analysis/*/lag` | Analyses lag |

### 9.2 Taille des Fichiers

| Couche | Fichiers | Taille approximative |
|--------|----------|---------------------|
| Bronze | 3 CSV | ~5 MB |
| Silver | 2 JSON | ~17 MB |
| Gold | 3 JSON | ~2 MB |
| **Total** | **8 fichiers** | **~24 MB** |

## 10. Qualite des Donnees

### 10.1 Validation

- Schema JSON/CSV valide
- Dates coherentes (pas de futur)
- Pas de valeurs NaN dans les champs critiques
- Sentiment score entre -1 et +1

### 10.2 Tracabilite

Chaque enregistrement conserve:
- `unified_id`: Identifiant unique
- `source_platform`: Origine (reddit, twitter, kaggle)
- `created_date`: Date de creation originale
- `processed_date`: Date de traitement

## 11. Troubleshooting

### Donnees manquantes
```bash
# Verifier les fichiers Bronze
ls -la data/bronze/*/

# Verifier les fichiers Gold
ls -la data/gold/
```

### Erreur de parsing JSON
```python
# Les NaN sont remplaces par null
import json
data = json.loads(content.replace('NaN', 'null'))
```

### Reindexation complete
```bash
cd backend
python scripts/index_documents.py --clear --test
```
