# Crypto Sentiment Analysis - Backend API

API FastAPI pour le dashboard d'analyse de sentiment des cryptomonnaies avec chatbot RAG intelligent.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND API                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   FastAPI    │    │   Services   │    │     Data     │          │
│  │   Routers    │───▶│              │───▶│   JSON/CSV   │          │
│  │              │    │              │    │              │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────────────────────────────────────────────┐          │
│  │                    RAG CHATBOT                        │          │
│  │  Question → Embedding → Pinecone → LLM → Response    │          │
│  └──────────────────────────────────────────────────────┘          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Configuration

Créer un fichier `.env` dans le dossier `backend/` :

```bash
# Pinecone (Vector Database)
PINECONE_API_KEY=pcsk_xxx...
PINECONE_INDEX_NAME=crypto-sentiment-rag

# LLM Provider
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxx...
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
├── .env                      # Variables d'environnement (API keys)
├── requirements.txt          # Dépendances Python
├── test_api.sh               # Tests API REST
├── app/
│   ├── main.py               # Point d'entrée FastAPI + CORS
│   ├── core/
│   │   └── config.py         # Configuration (chemins JSON)
│   ├── api/routers/
│   │   ├── cryptos.py        # Endpoints /api/cryptos
│   │   ├── sentiment.py      # Endpoints /api/sentiment
│   │   ├── analysis.py       # Endpoints /api/analysis
│   │   ├── events.py         # Endpoints /api/events
│   │   └── chat.py           # Endpoints /api/chat (RAG)
│   ├── services/
│   │   └── data_service.py   # Service lecture fichiers JSON/CSV
│   └── rag/                  # Module RAG Chatbot
│       ├── config.py         # Configuration RAG
│       ├── logger.py         # Logging centralisé
│       ├── document_loader.py # Chargement documents
│       ├── chunker.py        # Découpage en chunks
│       ├── embedding_service.py # Génération embeddings
│       ├── pinecone_service.py  # Interface Pinecone
│       ├── retriever_service.py # Recherche documents
│       ├── llm_service.py    # Interface LLM (Groq)
│       ├── rag_service.py    # Orchestration pipeline
│       └── README.md         # Documentation RAG
├── scripts/
│   └── index_documents.py    # Script d'indexation Pinecone
├── tests/
│   └── rag/                  # Tests unitaires RAG
│       ├── run_all_tests.sh
│       ├── test_config.py
│       ├── test_document_loader.py
│       ├── test_chunker.py
│       ├── test_embedding.py
│       ├── test_pinecone.py
│       ├── test_retriever.py
│       ├── test_llm.py
│       ├── test_rag_service.py
│       └── test_api_chat.py
└── logs/
    └── rag.log               # Logs du système RAG
```

## Endpoints API

### Cryptos (`/api/cryptos`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/cryptos` | Liste des cryptos avec prix et variation 24h |
| GET | `/api/cryptos/{symbol}` | Détails d'une crypto avec prix |
| GET | `/api/cryptos/{symbol}/chart` | Historique prix pour graphique |

**Query params:** `?days=7` (1-365)

### Sentiment (`/api/sentiment`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/sentiment/global` | Sentiment global du marché |
| GET | `/api/sentiment/{symbol}/timeline` | Timeline sentiment (30 jours par défaut) |

**Query params:** `?days=7` (1-365)

### Analysis (`/api/analysis`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/analysis/{symbol}/correlation` | Corrélation Pearson sentiment/prix |
| GET | `/api/analysis/{symbol}/lag` | Analyse lag (daily, weekly, monthly) |
| GET | `/api/analysis/{symbol}/stats` | Statistiques complètes |
| GET | `/api/analysis/{symbol}/scatter` | Données scatter plot (sentiment vs prix) |

**Query params:** `?days=30` (1-365)

### Events (`/api/events`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/events` | Liste des posts/événements |
| GET | `/api/events/stats` | Statistiques (total, positive, negative, neutral) |

**Query params:** `?crypto=BTC&sentiment=positive&limit=50`

### Chat RAG (`/api/chat`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/chat/` | Envoyer une question au chatbot |
| GET | `/api/chat/health` | État du système RAG |
| GET | `/api/chat/suggestions` | Questions suggérées |

**Body (POST):**
```json
{
  "message": "Quel est le sentiment de Bitcoin?",
  "crypto": "BTC"  // optionnel
}
```

**Response:**
```json
{
  "question": "Quel est le sentiment de Bitcoin?",
  "answer": "Le sentiment actuel de Bitcoin est positif...",
  "sources": [
    {
      "id": "post_123",
      "type": "post",
      "crypto": "BTC",
      "text": "Bitcoin is bullish...",
      "score": 0.87
    }
  ],
  "metadata": {
    "num_sources": 5,
    "processing_time": 1.23,
    "model_used": "groq"
  }
}
```

## RAG Chatbot

### Pipeline

```
Question → Embedding → Pinecone Search → Documents → LLM → Réponse
            (MiniLM)     (Vector DB)                  (Groq)
```

### Indexation des documents

```bash
# Première indexation (supprimer + réindexer)
python scripts/index_documents.py --clear

# Indexer et tester
python scripts/index_documents.py --test

# Tester uniquement
python scripts/index_documents.py --test-only
```

### Documents indexés

| Type | Source | Quantité |
|------|--------|----------|
| `post` | Twitter/Reddit | ~22,000 |
| `daily_summary` | Résumés quotidiens | ~2,700 |
| `price` | Prix historiques | ~1,300 |
| `analysis` | Corrélations | 3 |
| `lag_analysis` | Analyses lag | 9 |
| `faq` | FAQ statiques | 2 |
| **Total** | | **~26,000** |

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

### Tests API REST
```bash
chmod +x test_api.sh
./test_api.sh
```

### Tests RAG
```bash
# Tous les tests RAG
bash tests/rag/run_all_tests.sh

# Tests individuels
bash tests/rag/test_config.sh
bash tests/rag/test_document_loader.sh
bash tests/rag/test_chunker.sh
bash tests/rag/test_embedding.sh
bash tests/rag/test_pinecone.sh
bash tests/rag/test_retriever.sh
bash tests/rag/test_llm.sh
bash tests/rag/test_rag_service.sh

# Test API chat (serveur requis)
bash tests/rag/test_api_chat.sh
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
curl "http://localhost:8000/api/events?crypto=SOL&limit=20"

# Chat RAG
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Quel est le sentiment de Bitcoin?"}'

# Health check RAG
curl http://localhost:8000/api/chat/health
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

### Chat RAG Health
```json
{
  "status": "ok",
  "components": {
    "rag_service": "ok",
    "retriever": "ok",
    "llm": "ok (groq)",
    "pinecone": "ok (24903 vectors)"
  }
}
```

## Tech Stack

- **FastAPI** - Framework API REST
- **Python 3.10+** - Langage principal
- **Pydantic** - Validation des données
- **sentence-transformers** - Embeddings (all-MiniLM-L6-v2)
- **Pinecone** - Base de données vectorielle
- **Groq** - LLM (Llama 3.3 70B)
