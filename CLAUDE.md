# CLAUDE.md - Crypto Sentiment Analysis

## Project Overview

Plateforme d'analyse de sentiment des cryptomonnaies avec extraction de données sociales (Twitter/Reddit), analyse NLP, et visualisation via dashboard React.

## Architecture

```
Frontend (React :3000) ──▶ Backend (FastAPI :8000) ──▶ Data (JSON/CSV)
```

## Tech Stack

### Backend API
- **FastAPI** - API REST
- **Python 3.10+** - Langage principal
- **Pydantic** - Validation données

### Frontend
- **React 18** - Dashboard UI
- **React Router v6** - Navigation SPA
- **Recharts** - Graphiques (LineChart, ScatterChart)

### Data Pipeline
- **Apache Airflow** - Orchestration
- **Hugging Face** - Modèles sentiment
- **Docker** - Containerisation

## Project Structure

```
Crypto_Analysis/
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── main.py             # Point d'entrée, CORS, routers
│   │   ├── core/config.py      # Chemins vers data/
│   │   ├── api/routers/        # Endpoints
│   │   │   ├── cryptos.py      # /api/cryptos
│   │   │   ├── sentiment.py    # /api/sentiment
│   │   │   ├── analysis.py     # /api/analysis
│   │   │   └── events.py       # /api/events
│   │   └── services/
│   │       └── data_service.py # Lecture JSON/CSV
│   ├── requirements.txt
│   ├── test_api.sh
│   └── README.md
├── dashboard/                  # Frontend React
│   └── src/
│       ├── components/         # Header, MetricCard, SentimentGauge, CryptoChart
│       ├── pages/              # Overview, Timeline, Analysis, Events
│       ├── data/mockData.js    # Données mock (à remplacer par API)
│       └── styles/
├── data/
│   ├── bronze/                 # Données brutes
│   │   ├── BTC/historical_prices.csv
│   │   ├── ETH/historical_prices.csv
│   │   └── SOL/historical_prices.csv
│   ├── silver/enriched_data/   # Posts enrichis
│   │   └── crypto_sent_enriched_price.json
│   └── gold/                   # Données analysées
│       ├── sentiment_timeseries.json
│       ├── sentiment_price_correlation.json
│       └── lag_analysis.json
├── extraction/                 # Extracteurs Twitter/Reddit
├── Finetuning/                 # Fine-tuning modèles NLP
└── airflow/                    # DAGs
```

## Key Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
./test_api.sh  # Tests
```

### Frontend
```bash
cd dashboard
npm install
npm start  # localhost:3000
```

## API Endpoints

### Cryptos
| Endpoint | Description |
|----------|-------------|
| `GET /api/cryptos` | Liste cryptos avec prix et variation 24h |
| `GET /api/cryptos/{symbol}` | Détails d'une crypto |
| `GET /api/cryptos/{symbol}/chart?days=7` | Historique prix |

### Sentiment
| Endpoint | Description |
|----------|-------------|
| `GET /api/sentiment/global` | Sentiment global marché |
| `GET /api/sentiment/{symbol}/timeline?days=30` | Timeline sentiment + MA7 |

### Analysis
| Endpoint | Description |
|----------|-------------|
| `GET /api/analysis/{symbol}/correlation` | Corrélation Pearson |
| `GET /api/analysis/{symbol}/lag` | Lag analysis (daily/weekly/monthly) |
| `GET /api/analysis/{symbol}/stats` | Stats complètes |
| `GET /api/analysis/{symbol}/scatter?days=30` | Données scatter plot |

### Events
| Endpoint | Description |
|----------|-------------|
| `GET /api/events?crypto=BTC&limit=50` | Posts/événements |
| `GET /api/events/stats` | Stats (total, positive, negative, neutral) |

## Data Sources

| Fichier | Endpoint |
|---------|----------|
| `data/bronze/{symbol}/historical_prices.csv` | `/api/cryptos/*` |
| `data/gold/sentiment_timeseries.json` | `/api/sentiment/*` |
| `data/gold/sentiment_price_correlation.json` | `/api/analysis/*/correlation` |
| `data/gold/lag_analysis.json` | `/api/analysis/*/lag` |
| `data/silver/enriched_data/crypto_sent_enriched_price.json` | `/api/events` |

## Cryptocurrencies

- **BTC** - Bitcoin
- **ETH** - Ethereum
- **SOL** - Solana

## Notes for Claude

- Backend lit directement les fichiers JSON/CSV (pas de base de données)
- Les fichiers JSON peuvent contenir des `NaN` → remplacés par `null`
- Sentiment scores: 0 à 1 (API) ou -100 à +100 (Frontend)
- Frontend utilise encore mockData.js → à connecter à l'API
- Design: glassmorphism, dark theme
- Projet bilingue (FR/EN)

## Common Tasks

### Ajouter un nouvel endpoint
1. Créer méthode dans `backend/app/services/data_service.py`
2. Créer route dans `backend/app/api/routers/`
3. Tester avec `./test_api.sh`

### Connecter Frontend à l'API
1. Remplacer imports de `mockData.js` par appels `fetch()`
2. Base URL: `http://localhost:8000/api`
