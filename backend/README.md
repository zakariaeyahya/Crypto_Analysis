# Crypto Dashboard - Backend API

API FastAPI pour le dashboard d'analyse de sentiment des cryptomonnaies.

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Lancer le serveur

```bash
uvicorn app.main:app --reload --port 8000
```

Le serveur sera disponible sur http://localhost:8000

## Documentation API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Structure

```
backend/
├── requirements.txt
└── app/
    ├── main.py                 # Point d'entrée FastAPI
    ├── core/
    │   └── config.py           # Configuration (chemins JSON)
    ├── api/routers/
    │   ├── cryptos.py          # Endpoints /api/cryptos
    │   ├── sentiment.py        # Endpoints /api/sentiment
    │   ├── analysis.py         # Endpoints /api/analysis
    │   └── events.py           # Endpoints /api/events
    └── services/
        └── data_service.py     # Service lecture fichiers JSON
```

## Endpoints

### Cryptos

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/cryptos` | Liste des cryptos avec prix et variation 24h |
| GET | `/api/cryptos/{symbol}` | Détails d'une crypto avec prix |
| GET | `/api/cryptos/{symbol}/chart` | Historique prix pour graphique |

**Query params:** `?days=7` (1-365)

### Sentiment

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/sentiment/global` | Sentiment global du marché |
| GET | `/api/sentiment/{symbol}/timeline` | Timeline sentiment (30 jours par défaut) |

**Query params:** `?days=7` (1-365)

### Analysis

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/analysis/{symbol}/correlation` | Corrélation Pearson sentiment/prix |
| GET | `/api/analysis/{symbol}/lag` | Analyse lag (daily, weekly, monthly) |
| GET | `/api/analysis/{symbol}/stats` | Statistiques complètes |
| GET | `/api/analysis/{symbol}/scatter` | Données scatter plot (sentiment vs prix) |

**Query params:** `?days=30` (1-365)

### Events

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/events` | Liste des posts/événements |
| GET | `/api/events/stats` | Statistiques (total, positive, negative, neutral) |

**Query params:** `?crypto=BTC&sentiment=positive&limit=50`

## Sources de données

L'API lit directement les fichiers générés par le pipeline :

| Fichier | Endpoint |
|---------|----------|
| `data/bronze/{symbol}/historical_prices.csv` | `/api/cryptos/*` |
| `data/gold/sentiment_timeseries.json` | `/api/sentiment/*` |
| `data/gold/sentiment_price_correlation.json` | `/api/analysis/*/correlation` |
| `data/gold/lag_analysis.json` | `/api/analysis/*/lag` |
| `data/silver/enriched_data/crypto_sent_enriched_price.json` | `/api/events` |

## Tests

```bash
chmod +x test_api.sh
./test_api.sh
```

## Exemples de requêtes

```bash
# Sentiment global
curl http://localhost:8000/api/sentiment/global

# Timeline Bitcoin 30 jours
curl http://localhost:8000/api/sentiment/BTC/timeline?days=30

# Corrélation Ethereum
curl http://localhost:8000/api/analysis/ETH/correlation

# Events Solana
curl http://localhost:8000/api/events?crypto=SOL&limit=20
```

## Réponses type

### Sentiment Global
```json
{
  "score": 0.2534,
  "label": "Neutral"
}
```

### Correlation
```json
{
  "crypto": "Bitcoin",
  "pearson_r": -0.0795,
  "p_value": 0.0021,
  "n_observations": 1489
}
```

### Lag Analysis
```json
[
  {
    "crypto": "Bitcoin",
    "time_scale": "daily (D → D+1)",
    "pearson_r": 0.0371,
    "spearman_r": 0.0123,
    "granger_p_value": 0.4067,
    "n_observations": 1488
  }
]
```
