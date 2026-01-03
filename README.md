# Crypto Sentiment Analysis

Plateforme d'analyse de sentiment des cryptomonnaies (Bitcoin, Ethereum, Solana) basée sur les données Twitter et Reddit, avec un **chatbot RAG intelligent** incluant mémoire conversationnelle et reformulation de requêtes.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │───▶│   Backend   │───▶│    Data     │    │  Pinecone   │
│   React     │    │   FastAPI   │    │  JSON/CSV   │    │  (Vectors)  │
│   :3000     │    │   :8000     │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │                                     ▲
                          │         ┌─────────────┐             │
                          └────────▶│  RAG Module │─────────────┘
                                    │  + Memory   │
                                    │  + Groq LLM │
                                    └─────────────┘
```

## Features

- **Dashboard interactif** - Visualisation sentiment, prix, corrélations
- **Chatbot RAG intelligent** - Questions/réponses sur les cryptos
- **Mémoire conversationnelle** - Le chatbot garde le contexte (10 messages, 30 min)
- **Reformulation automatique** - Requêtes vagues enrichies ("Pourquoi?" → question complète)
- **Évaluation RAGAS** - Métriques de qualité du système RAG

## Quick Start

### 1. Backend API

```bash
cd backend

# Installation
pip install -r requirements.txt

# Configuration (.env)
cp .env.example .env
# Ajouter: PINECONE_API_KEY, GROQ_API_KEY

# Lancement
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

### 3. Indexation RAG (première fois)

```bash
cd backend
python scripts/index_documents.py --clear --test
```

## Structure du Projet

```
Crypto_Analysis/
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── main.py             # Point d'entrée
│   │   ├── api/routers/        # Endpoints API
│   │   │   ├── cryptos.py      # /api/cryptos
│   │   │   ├── sentiment.py    # /api/sentiment
│   │   │   ├── analysis.py     # /api/analysis
│   │   │   ├── events.py       # /api/events
│   │   │   └── chat.py         # /api/chat (RAG)
│   │   ├── services/           # Lecture données
│   │   └── rag/                # Module RAG
│   │       ├── config.py       # Configuration
│   │       ├── prompts.py      # Prompts externalisés
│   │       ├── memory_service.py   # Mémoire conversation
│   │       ├── rag_service.py  # Pipeline + reformulation
│   │       └── evaluation/     # Module RAGAS
│   ├── scripts/
│   │   ├── index_documents.py  # Indexation Pinecone
│   │   └── evaluate_rag.py     # Évaluation RAGAS
│   └── requirements.txt
├── dashboard/                  # Frontend React
│   └── src/
│       ├── api/index.js        # Appels API
│       ├── components/
│       │   └── Chatbot.jsx     # Chatbot avec mémoire
│       └── pages/              # Overview, Timeline, Analysis, Events
├── data/
│   ├── bronze/                 # Données brutes (prix CSV)
│   ├── silver/                 # Données enrichies (posts)
│   └── gold/                   # Données analysées (sentiment)
├── CLAUDE.md                   # Guide développeur complet
└── README.md                   # Ce fichier
```

## API Endpoints

### Données

| Endpoint | Description |
|----------|-------------|
| `GET /api/cryptos` | Prix actuels + variation 24h |
| `GET /api/cryptos/{symbol}/chart` | Historique prix |
| `GET /api/sentiment/global` | Sentiment global marché |
| `GET /api/sentiment/{symbol}/timeline` | Timeline sentiment |
| `GET /api/analysis/{symbol}/correlation` | Corrélation sentiment/prix |
| `GET /api/events` | Posts/événements crypto |

### Chatbot RAG

| Endpoint | Description |
|----------|-------------|
| `POST /api/chat/` | Envoyer une question (avec session_id) |
| `POST /api/chat/clear` | Effacer historique session |
| `GET /api/chat/health` | État du système RAG |
| `GET /api/chat/suggestions` | Questions suggérées |

## Chatbot RAG

### Mémoire Conversationnelle

Le chatbot garde en mémoire les 10 derniers messages:

```
User: "Quel est le sentiment de Bitcoin?"
Bot: "Le sentiment BTC est positif à 0.67..."

User: "Et pour Ethereum?"
Bot: "Le sentiment ETH est à 0.55, moins positif que Bitcoin." ✓

User: "Pourquoi?"
Bot: "Bitcoin bénéficie d'une perception plus favorable car..." ✓
```

### Reformulation Automatique

Les requêtes vagues sont enrichies avec le contexte:

| Requête originale | Requête reformulée |
|-------------------|-------------------|
| "Pourquoi?" | "Pourquoi Bitcoin a ce sentiment? Explique les raisons." |
| "Et Solana?" | "Quel est le sentiment de Solana?" |
| "Lequel?" | "Quelle crypto a le meilleur sentiment? Compare les." |

### Configuration

```bash
# backend/.env
PINECONE_API_KEY=pcsk_xxx...
PINECONE_INDEX_NAME=crypto-sentiment-rag
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxx...
```

## Évaluation RAGAS

Mesurer la qualité du système RAG avec des métriques standardisées.

```bash
cd backend

# Évaluation rapide (5 samples)
python scripts/evaluate_rag.py --quick

# Évaluation complète
python scripts/evaluate_rag.py --full --samples 20

# Tester une question
python scripts/evaluate_rag.py --query "Quel est le sentiment de Bitcoin?"

# Stats du dataset
python scripts/evaluate_rag.py --stats
```

### Résultats Typiques

```
Score moyen: 0.721 (72.1%)

Question                                        | Score
------------------------------------------------|-------
Quel est le sentiment actuel de Bitcoin?        | 0.693
Compare le sentiment de Bitcoin et Ethereum     | 0.656
Y a-t-il une correlation sentiment/prix?        | 0.764
Quelle crypto a le meilleur sentiment?          | 0.775
```

## Technologies

### Backend
- **FastAPI** - API REST
- **Python 3.10+** - Langage principal
- **sentence-transformers** - Embeddings (all-MiniLM-L6-v2)
- **Pinecone** - Base de données vectorielle
- **Groq** - LLM (Llama 3.3 70B)

### Frontend
- **React 18** - Framework UI
- **Recharts** - Graphiques
- **React Router** - Navigation

### ML/NLP
- **Hugging Face Transformers** - Modèles NLP
- **PyTorch** - Deep Learning

## Tests

```bash
# Backend API
cd backend
./test_api.sh

# Tests RAG
bash tests/rag/run_all_tests.sh

# Évaluation RAGAS
python scripts/evaluate_rag.py --quick
```

## Documentation

- [CLAUDE.md](CLAUDE.md) - Guide développeur complet
- [PR_DESCRIPTION.txt](PR_DESCRIPTION.txt) - Description des changements

## Cryptomonnaies Supportées

| Symbol | Name |
|--------|------|
| BTC | Bitcoin |
| ETH | Ethereum |
| SOL | Solana |

## License

MIT License - voir [LICENSE](LICENSE)
