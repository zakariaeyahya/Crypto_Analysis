# Crypto Sentiment Analysis

Plateforme d'analyse de sentiment des cryptomonnaies (Bitcoin, Ethereum, Solana) basée sur les données Twitter et Reddit.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │───▶│   Backend   │───▶│    Data     │
│   React     │    │   FastAPI   │    │  JSON/CSV   │
│   :3000     │    │   :8000     │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Quick Start

### 1. Backend API

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API disponible sur http://localhost:8000/docs

### 2. Frontend Dashboard

```bash
cd dashboard
npm install
npm start
```

Dashboard disponible sur http://localhost:3000

## Structure du Projet

```
Crypto_Analysis/
├── backend/                # API FastAPI
│   ├── app/
│   │   ├── main.py         # Point d'entrée
│   │   ├── api/routers/    # Endpoints API
│   │   └── services/       # Lecture données
│   └── requirements.txt
├── dashboard/              # Frontend React
│   └── src/
│       ├── components/     # Composants UI
│       └── pages/          # Pages (Overview, Timeline, Analysis, Events)
├── data/
│   ├── bronze/             # Données brutes (prix CSV, tweets)
│   ├── silver/             # Données nettoyées (enriched posts)
│   └── gold/               # Données analysées (sentiment, corrélation)
├── extraction/             # Scripts d'extraction Twitter/Reddit
├── Finetuning/             # Fine-tuning modèles NLP
└── airflow/                # DAGs Airflow
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/cryptos` | Prix actuels + variation 24h |
| `GET /api/cryptos/{symbol}/chart` | Historique prix |
| `GET /api/sentiment/global` | Sentiment global marché |
| `GET /api/sentiment/{symbol}/timeline` | Timeline sentiment |
| `GET /api/analysis/{symbol}/correlation` | Corrélation sentiment/prix |
| `GET /api/analysis/{symbol}/scatter` | Données scatter plot |
| `GET /api/events` | Posts/événements crypto |

## Data Pipeline

1. **Extraction** → `data/bronze/` (tweets, prix historiques)
2. **Cleaning** → `data/silver/` (posts enrichis avec sentiment)
3. **Analysis** → `data/gold/` (corrélations, timeseries)
4. **API** → Backend FastAPI lit les fichiers JSON/CSV
5. **Visualization** → Dashboard React affiche les données

## Technologies

- **Backend**: FastAPI, Python 3.10+
- **Frontend**: React 18, Recharts, React Router
- **ML/NLP**: Hugging Face Transformers, PyTorch
- **Orchestration**: Apache Airflow, Docker

## Tests

```bash
# Backend
cd backend
./test_api.sh

# Ou manuellement
curl http://localhost:8000/api/cryptos
curl http://localhost:8000/api/sentiment/global
```

## Documentation

- [Backend README](backend/README.md)
- [Dashboard README](dashboard/README.md)
