# RAG Chatbot - Documentation Technique

## Vue d'ensemble

Ce Pull Request introduit un **système de chatbot RAG (Retrieval-Augmented Generation)** complet pour l'analyse de sentiment des cryptomonnaies. Le chatbot permet aux utilisateurs de poser des questions en langage naturel sur Bitcoin, Ethereum et Solana, et reçoit des réponses contextualisées basées sur les données du projet.

## Architecture du système RAG

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE RAG                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Question │───▶│ Embedding│───▶│ Pinecone │───▶│ Documents│          │
│  │ utilisat.│    │ MiniLM   │    │ Search   │    │ pertinent│          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│                                                        │                 │
│                                                        ▼                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────┐              │
│  │ Réponse  │◀───│ Groq LLM │◀───│ Contexte formaté     │              │
│  │ finale   │    │ Llama 3.3│    │ (documents + méta)   │              │
│  └──────────┘    └──────────┘    └──────────────────────┘              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Fichiers ajoutés

### 1. Configuration (`backend/app/rag/config.py`)

Configuration centralisée du système RAG :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `PINECONE_API_KEY` | env | Clé API Pinecone |
| `PINECONE_INDEX_NAME` | `crypto-sentiment-rag` | Nom de l'index vectoriel |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Modèle d'embedding |
| `EMBEDDING_DIMENSION` | `384` | Dimension des vecteurs |
| `LLM_PROVIDER` | `groq` | Fournisseur LLM |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Modèle Groq |
| `RAG_TOP_K` | `5` | Nombre de documents récupérés |
| `RAG_MIN_SCORE` | `0.5` | Score minimum de similarité |

### 2. Chargement des documents (`backend/app/rag/document_loader.py`)

Charge les données depuis les fichiers JSON/CSV et les transforme en documents indexables :

| Méthode | Source | Type de document |
|---------|--------|------------------|
| `load_posts()` | `silver/enriched_data/crypto_sent_enriched_price.json` | `post` |
| `load_timeseries()` | `gold/sentiment_timeseries.json` | `daily_summary` |
| `load_correlations()` | `gold/sentiment_price_correlation.json` | `analysis` |
| `load_lag_analysis()` | `gold/lag_analysis.json` | `lag_analysis` |
| `load_prices()` | `bronze/{BTC,ETH,SOL}/historical_prices.csv` | `price` |
| `load_faq()` | FAQ statiques | `faq` |

### 3. Découpage en chunks (`backend/app/rag/chunker.py`)

Découpe les documents longs en morceaux optimisés pour la recherche :

- **Taille chunk** : 500 caractères max
- **Overlap** : 50 mots (chevauchement entre chunks)
- **Découpage** : Par phrases (évite de couper au milieu d'une phrase)

### 4. Service d'embedding (`backend/app/rag/embedding_service.py`)

Convertit le texte en vecteurs numériques :

- **Modèle** : `all-MiniLM-L6-v2` (sentence-transformers)
- **Dimension** : 384
- **Batch size** : 64 textes par batch
- **Normalisation** : Vecteurs normalisés (L2)

### 5. Service Pinecone (`backend/app/rag/pinecone_service.py`)

Interface avec la base de données vectorielle Pinecone :

| Méthode | Description |
|---------|-------------|
| `connect()` | Connexion à Pinecone, création de l'index si inexistant |
| `upsert_chunks()` | Indexation des chunks avec embeddings |
| `search()` | Recherche par similarité cosinus |
| `delete_all()` | Suppression de tous les vecteurs |
| `get_stats()` | Statistiques de l'index |

### 6. Service de retrieval (`backend/app/rag/retriever_service.py`)

Recherche les documents pertinents pour une question :

- **Auto-détection crypto** : Détecte BTC/ETH/SOL dans la question
- **Filtrage** : Par crypto, type de document, source, date
- **Score minimum** : Filtre les résultats < 0.5 de similarité
- **Contexte formaté** : Prépare le contexte pour le LLM

### 7. Service LLM (`backend/app/rag/llm_service.py`)

Interface avec les modèles de langage :

| Provider | Modèle | Status |
|----------|--------|--------|
| Groq | `llama-3.3-70b-versatile` | Principal |
| OpenAI | `gpt-3.5-turbo` | Alternative |
| Ollama | `mistral` | Local (fallback) |

**System prompt** :
```
Tu es un assistant expert en analyse de cryptomonnaies.
Tu analyses les sentiments du marché crypto basés sur les données Twitter et Reddit.
Réponds UNIQUEMENT en utilisant les informations du contexte fourni.
```

### 8. Orchestration RAG (`backend/app/rag/rag_service.py`)

Orchestre le pipeline RAG complet :

```python
def process_query(question, crypto=None, top_k=None):
    # 1. Retrieval - Récupérer les documents pertinents
    # 2. Vérifier si documents trouvés
    # 3. Generation - Générer la réponse avec LLM
    # 4. Construire la réponse finale avec sources
```

**Fonctionnalités** :
- `process_query()` : Pipeline RAG complet
- `get_quick_answer()` : Réponse simple sans métadonnées
- `get_crypto_summary()` : Résumé complet d'une crypto
- `compare_cryptos()` : Comparaison de plusieurs cryptos
- `health_check()` : Vérification de l'état du système

### 9. Router API Chat (`backend/app/api/routers/chat.py`)

Endpoints REST pour le chatbot :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/chat/` | POST | Envoyer une question au chatbot |
| `/api/chat/health` | GET | État du système RAG |
| `/api/chat/suggestions` | GET | Questions suggérées |

**Exemple de requête** :
```json
POST /api/chat/
{
    "message": "Quel est le sentiment de Bitcoin?",
    "crypto": "BTC"  // optionnel
}
```

**Exemple de réponse** :
```json
{
    "question": "Quel est le sentiment de Bitcoin?",
    "answer": "Le sentiment actuel de Bitcoin est...",
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

### 10. Script d'indexation (`backend/scripts/index_documents.py`)

Script CLI pour indexer les documents dans Pinecone :

```bash
# Indexation normale
python scripts/index_documents.py

# Supprimer l'index et réindexer
python scripts/index_documents.py --clear

# Indexer puis tester
python scripts/index_documents.py --test

# Tester seulement (pas d'indexation)
python scripts/index_documents.py --test-only
```

**Pipeline d'indexation** :
1. Charger les documents (posts, timeseries, correlations, prix, FAQ)
2. Découper en chunks (500 caractères max)
3. Générer les embeddings (all-MiniLM-L6-v2)
4. Connexion à Pinecone
5. Upsert des vecteurs par batches de 100

## Configuration requise

### Variables d'environnement (`.env`)

```bash
# Pinecone
PINECONE_API_KEY=pcsk_xxx...
PINECONE_INDEX_NAME=crypto-sentiment-rag

# LLM (Groq recommandé)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxx...
```

### Dépendances Python

```
sentence-transformers>=2.2.0
pinecone-client>=3.0.0
groq>=0.4.0
python-dotenv>=1.0.0
```

## Utilisation

### 1. Indexation initiale

```bash
cd backend
python scripts/index_documents.py --clear --test
```

### 2. Démarrage de l'API

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Test du chatbot

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Quel est le sentiment de Bitcoin?"}'
```

## Statistiques de l'index

- **Documents indexés** : ~26,000 vecteurs
- **Types** : posts, daily_summary, analysis, price, faq, lag_analysis
- **Dimension** : 384
- **Métrique** : Similarité cosinus

## Logging

Les logs sont centralisés dans `backend/logs/rag.log` :
- Niveau INFO pour les opérations normales
- Niveau DEBUG pour le détail des recherches
- Niveau ERROR pour les erreurs

## Points clés

1. **Lazy loading** : Les services sont initialisés uniquement à la première utilisation
2. **Singleton pattern** : Une seule instance de chaque service
3. **Fallback** : Si le LLM échoue, une réponse basique est générée
4. **Filtrage intelligent** : Auto-détection de la crypto dans la question
5. **Sources traçables** : Chaque réponse inclut les documents sources avec scores
