# Architecture du Systeme - CryptoVibe

## 1. Vue d'Ensemble

CryptoVibe est une plateforme d'analyse de sentiment des cryptomonnaies (Bitcoin, Ethereum, Solana) basee sur les donnees des reseaux sociaux, avec un chatbot RAG intelligent.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          ARCHITECTURE GLOBALE                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────┐                                                               │
│   │   Sources   │                                                               │
│   │   Donnees   │                                                               │
│   └──────┬──────┘                                                               │
│          │                                                                       │
│          ▼                                                                       │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│   │   Airflow   │───▶│   Bronze    │───▶│   Silver    │───▶│    Gold     │     │
│   │ Orchestrator│    │  (Brut)     │    │ (Enrichi)   │    │ (Analyse)   │     │
│   └─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘     │
│                                                                    │            │
│                      ┌────────────────────────────────────────────┘            │
│                      │                                                          │
│                      ▼                                                          │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                        │
│   │  Pinecone   │◀───│   FastAPI   │◀───│    React    │                        │
│   │  (Vectors)  │    │   Backend   │    │  Dashboard  │                        │
│   └──────┬──────┘    └──────┬──────┘    └─────────────┘                        │
│          │                  │                                                   │
│          │           ┌──────┴──────┐                                           │
│          └──────────▶│  RAG + LLM  │                                           │
│                      │   (Groq)    │                                           │
│                      └─────────────┘                                           │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Composants du Systeme

### 2.1 Vue en Couches

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   React Dashboard                        │    │
│  │  • Overview    • Timeline    • Analysis    • Chatbot    │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                         API LAYER                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    FastAPI Backend                       │    │
│  │  /cryptos    /sentiment    /analysis    /events   /chat │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                       SERVICE LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ DataService  │  │  RAGService  │  │MemoryService │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
├─────────────────────────────────────────────────────────────────┤
│                        DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  JSON/CSV    │  │   Pinecone   │  │  In-Memory   │          │
│  │  (Files)     │  │  (Vectors)   │  │  (Sessions)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Composants Principaux

| Composant | Technologie | Role |
|-----------|-------------|------|
| **Frontend** | React 18 | Interface utilisateur |
| **Backend** | FastAPI | API REST |
| **Stockage** | JSON/CSV | Donnees structurees |
| **Vecteurs** | Pinecone | Recherche semantique |
| **LLM** | Groq (Llama 3.3) | Generation de reponses |
| **Orchestration** | Airflow | Pipeline automatise |

---

## 3. Architecture des Donnees

### 3.1 Architecture Medallion

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEDALLION ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SOURCES                 BRONZE              SILVER              │
│  ┌────────┐           ┌─────────┐         ┌─────────┐           │
│  │ Reddit │──────────▶│  Posts  │────────▶│ Posts   │           │
│  │ (PRAW) │           │  bruts  │         │ + NER   │           │
│  └────────┘           │  JSON   │         │ + Sent. │           │
│                       └─────────┘         └────┬────┘           │
│  ┌────────┐           ┌─────────┐              │                │
│  │ Kaggle │──────────▶│ Tweets  │──────────────┤                │
│  │ Tweets │           │  CSV    │              │                │
│  └────────┘           └─────────┘              │                │
│                                                │                 │
│  ┌────────┐           ┌─────────┐              │      GOLD      │
│  │ Yahoo  │──────────▶│  Prix   │              │   ┌─────────┐  │
│  │Finance │           │  OHLC   │──────────────┼──▶│Timeseries│  │
│  └────────┘           │  CSV    │              │   │Correlat. │  │
│                       └─────────┘              │   │Lag Anal. │  │
│                                                │   └─────────┘  │
│                                                │        │       │
│                                                └────────┼───────│
│                                                         ▼       │
│                                                   ┌──────────┐  │
│                                                   │ Pinecone │  │
│                                                   │ ~26k vec │  │
│                                                   └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Structure des Fichiers

```
data/
├── bronze/                      # Donnees brutes
│   ├── BTC/
│   │   └── historical_prices.csv
│   ├── ETH/
│   │   └── historical_prices.csv
│   └── SOL/
│       └── historical_prices.csv
│
├── silver/                      # Donnees enrichies
│   └── enriched_data/
│       ├── enriched_data.json
│       └── crypto_sent_enriched_price.json
│
└── gold/                        # Donnees analysees
    ├── sentiment_timeseries.json
    ├── sentiment_price_correlation.json
    └── lag_analysis.json
```

---

## 4. Architecture Backend

### 4.1 Structure des Modules

```
backend/
├── app/
│   ├── main.py                 # Point d'entree FastAPI
│   ├── core/
│   │   └── config.py           # Configuration
│   │
│   ├── api/routers/            # Endpoints REST
│   │   ├── cryptos.py          # /api/cryptos
│   │   ├── sentiment.py        # /api/sentiment
│   │   ├── analysis.py         # /api/analysis
│   │   ├── events.py           # /api/events
│   │   └── chat.py             # /api/chat
│   │
│   ├── services/
│   │   └── data_service.py     # Lecture fichiers
│   │
│   └── rag/                    # Module RAG
│       ├── config.py
│       ├── prompts.py
│       ├── embedding_service.py
│       ├── pinecone_service.py
│       ├── retriever_service.py
│       ├── llm_service.py
│       ├── memory_service.py
│       ├── rag_service.py
│       └── evaluation/
│
├── scripts/
│   ├── index_documents.py
│   └── evaluate_rag.py
│
└── tests/
```

### 4.2 Flux de Requete API

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Client  │───▶│  Router  │───▶│ Service  │───▶│   Data   │
│  (HTTP)  │    │ (FastAPI)│    │  Layer   │    │  Files   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │                                               │
     │◀──────────────────────────────────────────────┘
     │              JSON Response
```

---

## 5. Architecture RAG (Chatbot)

### 5.1 Pipeline RAG

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG PIPELINE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐                                                   │
│  │ Question │                                                   │
│  └────┬─────┘                                                   │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────┐    ┌─────────────┐                             │
│  │  Memory     │───▶│Reformulation│  (si question vague)        │
│  │  Service    │    │   Query     │                             │
│  └─────────────┘    └──────┬──────┘                             │
│                            │                                     │
│                            ▼                                     │
│                     ┌─────────────┐                             │
│                     │  Embedding  │  all-MiniLM-L6-v2           │
│                     │   Service   │  384 dimensions             │
│                     └──────┬──────┘                             │
│                            │                                     │
│                            ▼                                     │
│                     ┌─────────────┐                             │
│                     │  Pinecone   │  ~26,000 vecteurs           │
│                     │   Search    │  top_k=5, min_score=0.35    │
│                     └──────┬──────┘                             │
│                            │                                     │
│                            ▼                                     │
│                     ┌─────────────┐                             │
│                     │  Retriever  │  Documents pertinents       │
│                     │   Service   │                             │
│                     └──────┬──────┘                             │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Prompt    │───▶│     LLM     │───▶│   Reponse   │         │
│  │  Template   │    │    Groq     │    │  Formatee   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Composants RAG

| Composant | Fichier | Role |
|-----------|---------|------|
| **EmbeddingService** | `embedding_service.py` | Vectorisation (MiniLM) |
| **PineconeService** | `pinecone_service.py` | Stockage/recherche vecteurs |
| **RetrieverService** | `retriever_service.py` | Recuperation documents |
| **LLMService** | `llm_service.py` | Generation (Groq) |
| **MemoryService** | `memory_service.py` | Historique conversation |
| **RAGService** | `rag_service.py` | Orchestration pipeline |

### 5.3 Memoire Conversationnelle

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEMORY SERVICE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Session Storage (Dict Python)                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  session_id: {                                           │   │
│  │    messages: [                                           │   │
│  │      {role: "user", content: "Sentiment BTC?"},         │   │
│  │      {role: "assistant", content: "Le sentiment..."},   │   │
│  │      ...                                                 │   │
│  │    ],                                                    │   │
│  │    last_activity: datetime                               │   │
│  │  }                                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Configuration:                                                  │
│  • Max messages: 10                                             │
│  • Timeout: 30 minutes                                          │
│  • Cleanup automatique                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Architecture Frontend

### 6.1 Structure React

```
dashboard/src/
├── App.jsx                 # Routes + Layout
├── api/
│   └── index.js            # Client API
├── store/
│   └── CryptoContext.js    # State global
├── components/
│   ├── Header.jsx
│   ├── MetricCard.jsx
│   ├── SentimentGauge.jsx
│   ├── CryptoChart.jsx
│   ├── Chatbot.jsx
│   └── ChatbotWidget.jsx
└── pages/
    ├── Overview.jsx
    ├── Timeline.jsx
    ├── Analysis.jsx
    ├── Events.jsx
    └── About.jsx
```

### 6.2 Flux de Donnees React

```
┌─────────────────────────────────────────────────────────────────┐
│                     REACT DATA FLOW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │    API      │───▶│   Context   │───▶│   Pages     │         │
│  │   Client    │    │   (State)   │    │ Components  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                            │                   │                 │
│                            │                   │                 │
│                            ▼                   ▼                 │
│                     ┌─────────────┐    ┌─────────────┐         │
│                     │  Recharts   │    │   Lucide    │         │
│                     │  (Graphs)   │    │   (Icons)   │         │
│                     └─────────────┘    └─────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Architecture NLP

### 7.1 Pipeline de Traitement

```
┌─────────────────────────────────────────────────────────────────┐
│                      NLP PIPELINE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Texte   │───▶│Preprocess│───▶│Sentiment │───▶│   NER    │  │
│  │   Brut   │    │          │    │ RoBERTa  │    │ Dictio.  │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                                                                  │
│  Preprocessing:           Sentiment:           NER:             │
│  • Clean URLs             • RoBERTa Twitter    • Cryptos        │
│  • Remove mentions        • Fine-tuned         • Exchanges      │
│  • Normalize              • Binary (Pos/Neg)   • Influencers    │
│  • Keep emojis            • 70.1% accuracy     • 92.5% F1       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Modeles Utilises

| Modele | Usage | Performance |
|--------|-------|-------------|
| **RoBERTa Twitter** | Sentiment (fine-tuned) | 70.1% accuracy |
| **Hybrid VADER** | Baseline sentiment | 69.84% accuracy |
| **all-MiniLM-L6-v2** | Embeddings RAG | 384 dimensions |
| **Llama 3.3 70B** | Generation LLM | Via Groq |

---

## 8. Communication Inter-Composants

### 8.1 Protocoles

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMMUNICATION                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Frontend ◀────── HTTP/REST/JSON ──────▶ Backend                │
│                                                                  │
│  Backend ◀─────── gRPC (Pinecone) ──────▶ Pinecone              │
│                                                                  │
│  Backend ◀─────── HTTP/REST ────────────▶ Groq API              │
│                                                                  │
│  Airflow ◀─────── HTTP/REST ────────────▶ Reddit API            │
│                                                                  │
│  Airflow ◀─────── HTTP/REST ────────────▶ Yahoo Finance         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Ports et URLs

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Frontend | 3000 | http://localhost:3000 |
| Swagger Docs | 8000 | http://localhost:8000/docs |
| Airflow UI | 8080 | http://localhost:8080 |

---

## 9. Securite

### 9.1 Authentification

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITE                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  API Keys (stockees dans .env):                                 │
│  • PINECONE_API_KEY                                             │
│  • GROQ_API_KEY                                                 │
│  • REDDIT_CLIENT_ID / SECRET                                    │
│                                                                  │
│  CORS:                                                          │
│  • Origine autorisee: localhost:3000                            │
│                                                                  │
│  Validation:                                                     │
│  • Pydantic pour validation des inputs                          │
│  • HTTPException pour gestion erreurs                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Scalabilite

### 10.1 Points d'Extension

| Composant | Scalabilite |
|-----------|-------------|
| **Backend** | Horizontal (multiple instances Uvicorn) |
| **Pinecone** | Cloud-native, auto-scaling |
| **Groq** | API cloud, rate limits |
| **Donnees** | Ajout nouvelles cryptos |
| **Sources** | Ajout nouveaux scrapers |

### 10.2 Limites Actuelles

| Ressource | Limite |
|-----------|--------|
| Memoire sessions | In-memory (non persistant) |
| Historique | 10 messages / session |
| Rate limit Groq | Selon plan |
| Pinecone vecteurs | ~26,000 |

---

## 11. Diagramme de Deploiement

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOIEMENT                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LOCAL DEVELOPMENT                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐             │   │
│  │  │ React   │    │ FastAPI │    │ Airflow │             │   │
│  │  │ :3000   │    │ :8000   │    │ :8080   │             │   │
│  │  └─────────┘    └─────────┘    └─────────┘             │   │
│  │                      │              │                   │   │
│  │                      ▼              ▼                   │   │
│  │              ┌─────────────────────────┐               │   │
│  │              │    data/ (JSON/CSV)     │               │   │
│  │              └─────────────────────────┘               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  CLOUD SERVICES                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐             │   │
│  │  │Pinecone │    │  Groq   │    │ Reddit  │             │   │
│  │  │  Cloud  │    │   API   │    │   API   │             │   │
│  │  └─────────┘    └─────────┘    └─────────┘             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 12. Stack Technologique Resume

### Backend
| Categorie | Technologie |
|-----------|-------------|
| Framework | FastAPI 0.109.0 |
| Serveur | Uvicorn 0.27.0 |
| Validation | Pydantic 2.5.3 |
| Embeddings | sentence-transformers |
| Vector DB | Pinecone 3.0.0 |
| LLM | Groq (Llama 3.3 70B) |

### Frontend
| Categorie | Technologie |
|-----------|-------------|
| Framework | React 18.2.0 |
| Routing | React Router 6.20.0 |
| Graphiques | Recharts 2.10.0 |
| Icones | Lucide React 0.562.0 |

### Data Pipeline
| Categorie | Technologie |
|-----------|-------------|
| Orchestration | Apache Airflow |
| Stockage | JSON/CSV (Medallion) |
| NLP | RoBERTa, VADER, spaCy |
| Prix | yfinance |
