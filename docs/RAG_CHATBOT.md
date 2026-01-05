# Documentation RAG Chatbot - CryptoVibe

## 1. Introduction

Le chatbot RAG (Retrieval-Augmented Generation) de CryptoVibe est un assistant intelligent specialise dans l'analyse de sentiment des cryptomonnaies. Il combine la recherche semantique (Pinecone) avec un LLM (Groq/Llama) pour fournir des reponses contextualisees.

### Fonctionnalites Principales

- Reponses basees sur les donnees reelles (sentiment, prix, correlations)
- Memoire conversationnelle (10 messages, 30 min timeout)
- Reformulation automatique des questions vagues
- Support de 3 cryptomonnaies: Bitcoin, Ethereum, Solana
- Systeme de feedback utilisateur (thumbs up/down)

---

## 2. Architecture

### 2.1 Pipeline RAG Complet

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            RAG PIPELINE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐                                                               │
│  │ Question │                                                               │
│  │ (User)   │                                                               │
│  └────┬─────┘                                                               │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────┐     ┌─────────────┐                                        │
│  │   Memory    │────▶│Reformulation│  "Et Solana?" → "Quel est le          │
│  │  Service    │     │  (si vague) │   sentiment de Solana?"                │
│  └─────────────┘     └──────┬──────┘                                        │
│                             │                                                │
│                             ▼                                                │
│                      ┌─────────────┐                                        │
│                      │  Embedding  │  all-MiniLM-L6-v2                      │
│                      │   Service   │  384 dimensions                        │
│                      └──────┬──────┘                                        │
│                             │                                                │
│                             ▼                                                │
│                      ┌─────────────┐                                        │
│                      │  Pinecone   │  ~26,000 vecteurs                      │
│                      │   Search    │  top_k=5, min_score=0.35               │
│                      └──────┬──────┘                                        │
│                             │                                                │
│                             ▼                                                │
│                      ┌─────────────┐                                        │
│                      │  Retriever  │  Filtrage + Ranking                    │
│                      │   Service   │                                        │
│                      └──────┬──────┘                                        │
│                             │                                                │
│                             ▼                                                │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   System    │────▶│     LLM     │────▶│   Reponse   │                   │
│  │   Prompt    │     │    Groq     │     │  Formatee   │                   │
│  └─────────────┘     │ Llama 3.3   │     └─────────────┘                   │
│                      └─────────────┘                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Structure des Fichiers

```
backend/app/rag/
├── config.py              # Configuration (API keys, parametres)
├── prompts.py             # Prompts systeme et templates
├── logger.py              # Logging centralise
├── memory_service.py      # Memoire conversationnelle
├── document_loader.py     # Chargement des donnees
├── chunker.py             # Decoupage en chunks
├── embedding_service.py   # Vectorisation (MiniLM)
├── pinecone_service.py    # Interface Pinecone
├── retriever_service.py   # Recherche de documents
├── llm_service.py         # Interface LLM (Groq)
├── rag_service.py         # Orchestration du pipeline
├── feedback_service.py    # Gestion des feedbacks
└── evaluation/            # Module RAGAS
    ├── ragas_evaluator.py
    └── test_dataset.json
```

---

## 3. Composants

### 3.1 Embedding Service

**Modele**: `all-MiniLM-L6-v2` (sentence-transformers)

| Parametre | Valeur |
|-----------|--------|
| Dimensions | 384 |
| Normalisation | L2 |
| Batch size | 32 |

```python
from app.rag.embedding_service import get_embedding_service

embedding_service = get_embedding_service()
vector = embedding_service.encode("Quel est le sentiment de Bitcoin?")
# vector.shape = (384,)
```

### 3.2 Pinecone Service

**Index**: `crypto-sentiment-rag`

| Parametre | Valeur |
|-----------|--------|
| Cloud | AWS |
| Region | us-east-1 |
| Metric | Cosine |
| Vectors | ~26,000 |

**Types de documents indexes**:
| Type | Description | Quantite |
|------|-------------|----------|
| `posts` | Posts Reddit/Twitter | ~22,000 |
| `daily_summary` | Resumes quotidiens | ~2,700 |
| `price` | Series de prix | ~1,300 |
| `analysis` | Correlations, stats | ~14 |
| `faq` | Questions frequentes | ~10 |

### 3.3 Retriever Service

**Configuration**:
```python
RAG_TOP_K = 5           # Nombre de documents recuperes
RAG_MIN_SCORE = 0.35    # Score minimum de similarite
```

**Fonctionnement**:
1. Encode la question en vecteur
2. Recherche dans Pinecone (top_k=5)
3. Filtre par score minimum (0.35)
4. Retourne les documents pertinents

### 3.4 LLM Service

**Provider**: Groq (Cloud)

| Parametre | Valeur |
|-----------|--------|
| Modele | Llama 3.3 70B Versatile |
| Temperature | 0.7 |
| Max tokens | 500 |

**Fallback**: Si Groq indisponible, retourne un message d'erreur gracieux.

### 3.5 Memory Service

**Memoire conversationnelle** pour comprendre le contexte.

| Parametre | Valeur |
|-----------|--------|
| Max messages | 10 par session |
| Timeout | 30 minutes |
| Stockage | In-memory (dict Python) |

**Structure de session**:
```python
{
    "session_id": {
        "messages": [
            {"role": "user", "content": "...", "timestamp": "..."},
            {"role": "assistant", "content": "...", "timestamp": "..."}
        ],
        "last_activity": datetime
    }
}
```

**Exemple de conversation avec memoire**:
```
User: "Quel est le sentiment de Bitcoin?"
Bot:  "Le sentiment de Bitcoin est positif a 0.15..."

User: "Et Ethereum?"  ← Question vague
Bot:  "Le sentiment d'Ethereum est a 0.08, moins positif que Bitcoin."

User: "Pourquoi?"  ← Utilise le contexte
Bot:  "Bitcoin beneficie d'une meilleure perception car..."
```

---

## 4. Reformulation de Requetes

### 4.1 Detection des Requetes Vagues

Le systeme detecte automatiquement les questions vagues:
- Moins de 3 mots
- Patterns: "pourquoi?", "et X?", "lequel?", "comment?"

### 4.2 Exemples de Reformulation

| Question originale | Question reformulee |
|-------------------|---------------------|
| "Pourquoi?" | "Pourquoi Bitcoin a ce sentiment? Explique les raisons." |
| "Et Solana?" | "Quel est le sentiment de Solana?" |
| "Lequel?" | "Quelle crypto a le meilleur sentiment? Compare les." |
| "Et les autres?" | "Quel est le sentiment des autres cryptos (ETH, SOL)?" |
| "Comment?" | "Comment evolue le sentiment? Explique la tendance." |

### 4.3 Algorithme

```python
def _reformulate_query(self, question: str, session_id: str) -> str:
    # 1. Detecter si reformulation necessaire
    if len(question.split()) >= 3 and not is_vague_pattern(question):
        return question

    # 2. Recuperer le contexte de l'historique
    history = self.memory.get_history(session_id)
    last_crypto = extract_crypto_from_history(history)
    last_topic = extract_topic_from_history(history)

    # 3. Enrichir la question
    return enrich_question(question, last_crypto, last_topic)
```

---

## 5. Prompts

### 5.1 System Prompt

```
Tu es un assistant expert en analyse de cryptomonnaies (Bitcoin, Ethereum, Solana).
Tu analyses les sentiments du marche crypto bases sur les donnees Twitter et Reddit.

REGLES IMPORTANTES:
1. Reponds UNIQUEMENT en utilisant les informations du contexte fourni
2. Si tu ne trouves pas l'information, dis-le clairement
3. Sois concis et precis (maximum 3-4 phrases)
4. Utilise des chiffres et pourcentages quand disponibles
5. Reponds en francais
6. NE MENTIONNE JAMAIS les sources, documents, scores ou IDs
7. Reponds directement comme si tu connaissais l'information
8. Utilise l'historique de conversation pour comprendre le contexte
```

### 5.2 User Prompt Template (sans historique)

```
Contexte (informations a utiliser pour repondre):
{context}

Question de l'utilisateur: {question}

Reponse (reponds directement sans mentionner les sources):
```

### 5.3 User Prompt Template (avec historique)

```
Historique de la conversation:
{history}

Contexte (informations a utiliser pour repondre):
{context}

Question actuelle de l'utilisateur: {question}

Reponse (utilise l'historique pour comprendre le contexte):
```

---

## 6. Configuration

### 6.1 Variables d'Environnement

```bash
# backend/.env

# Pinecone
PINECONE_API_KEY=pcsk_xxxxxxxxxxxxxxxx
PINECONE_INDEX_NAME=crypto-sentiment-rag

# LLM
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```

### 6.2 Parametres RAG (config.py)

```python
# Embedding
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# LLM
GROQ_MODEL = "llama-3.3-70b-versatile"

# RAG
RAG_TOP_K = 5           # Documents a recuperer
RAG_MIN_SCORE = 0.35    # Score minimum (abaisse pour meilleur recall)
```

### 6.3 Mapping Cryptos

```python
CRYPTO_MAPPING = {
    "Bitcoin": "BTC",
    "Ethereum": "ETH",
    "Solana": "SOL",
}
```

---

## 7. API Endpoints

### 7.1 Envoyer un Message

**POST** `/api/chat/`

```json
// Request
{
  "message": "Quel est le sentiment de Bitcoin?",
  "crypto": "BTC",
  "session_id": "user123_session456"
}

// Response
{
  "question": "Quel est le sentiment de Bitcoin?",
  "answer": "Le sentiment actuel de Bitcoin est positif avec un score de 0.15...",
  "sources": [
    {
      "id": "doc_123",
      "type": "daily_summary",
      "crypto": "BTC",
      "text": "Resume du 15 janvier...",
      "score": 0.85
    }
  ],
  "metadata": {
    "num_sources": 5,
    "processing_time": 0.45,
    "model_used": "groq/llama-3.3-70b",
    "session_id": "user123_session456",
    "has_history": true
  }
}
```

### 7.2 Effacer l'Historique

**POST** `/api/chat/clear`

```json
// Request
{"session_id": "user123_session456"}

// Response
{"status": "cleared", "session_id": "user123_session456"}
```

### 7.3 Suggestions

**GET** `/api/chat/suggestions`

```json
// Response
{
  "suggestions": [
    "Quel est le sentiment actuel de Bitcoin?",
    "Compare le sentiment de BTC et ETH",
    "Y a-t-il une correlation sentiment-prix?"
  ]
}
```

### 7.4 Health Check

**GET** `/api/chat/health`

```json
// Response
{
  "status": "healthy",
  "components": {
    "embeddings": "ok",
    "pinecone": "ok",
    "llm": "ok",
    "memory": "ok"
  }
}
```

### 7.5 Feedback

**POST** `/api/chat/feedback`

```json
// Request
{
  "message_id": "msg_001",
  "question": "Quel est le sentiment de BTC?",
  "answer": "Le sentiment est positif...",
  "feedback_type": "positive",
  "session_id": "user123"
}

// Response
{"status": "saved", "feedback_id": "fb_xyz789"}
```

---

## 8. Questions Suggerees

### 8.1 Categories

**Sentiment General**:
- "Quel est le sentiment actuel de Bitcoin?"
- "Comment evolue le sentiment Ethereum cette semaine?"
- "Quel est le sentiment global du marche crypto?"

**Comparaisons**:
- "Compare le sentiment de BTC et ETH"
- "Quelle crypto a le meilleur sentiment actuellement?"
- "Compare les sentiments de Bitcoin, Ethereum et Solana"

**Correlations**:
- "Y a-t-il une correlation entre sentiment et prix pour Bitcoin?"
- "Le sentiment influence-t-il le prix de Solana?"
- "Quelle est la correlation sentiment-prix pour ETH?"

**Tendances**:
- "Quelles sont les tendances recentes pour Bitcoin?"
- "Le sentiment de Solana est-il en hausse ou en baisse?"

**Analyses**:
- "Resume l'analyse de sentiment pour Bitcoin"
- "Donne-moi un apercu du marche crypto"

---

## 9. Indexation des Documents

### 9.1 Script d'Indexation

```bash
cd backend

# Indexer tous les documents (avec clear)
python scripts/index_documents.py --clear

# Tester l'indexation
python scripts/index_documents.py --test

# Voir les stats
python scripts/index_documents.py --stats
```

### 9.2 Types de Documents Indexes

| Source | Type | Champs |
|--------|------|--------|
| Posts enrichis | `posts` | text, sentiment, crypto, date |
| Timeseries | `daily_summary` | date, crypto, sentiment_mean |
| Correlations | `analysis` | crypto, pearson_r, p_value |
| Prix | `price` | date, crypto, price_close |
| FAQ | `faq` | question, answer |

### 9.3 Metadata des Vecteurs

```python
{
    "id": "post_abc123",
    "type": "posts",
    "crypto": "BTC",
    "date": "2024-01-15",
    "sentiment": "positive",
    "text": "Bitcoin looking bullish..."
}
```

---

## 10. Evaluation RAGAS

### 10.1 Metriques

| Metrique | Description | Score CryptoVibe |
|----------|-------------|------------------|
| Faithfulness | Fidelite aux sources | 74% |
| Answer Relevancy | Pertinence reponse | 71% |
| Context Precision | Precision contexte | 72% |
| **Score Global** | Moyenne | **72.1%** |

### 10.2 Dataset de Test

- 26 questions de test
- 7 categories
- 3 niveaux de difficulte

### 10.3 Commandes

```bash
cd backend

# Evaluation rapide
python scripts/evaluate_rag.py --quick

# Evaluation complete
python scripts/evaluate_rag.py --full --samples 20

# Tester une question
python scripts/evaluate_rag.py --query "Quel est le sentiment de Bitcoin?"
```

---

## 11. Frontend Integration

### 11.1 Composant Chatbot

**Fichier**: `dashboard/src/components/Chatbot.jsx`

**Fonctionnalites**:
- Session ID unique par conversation
- Bouton effacer (icone poubelle)
- Indicateur "Memoire active"
- Suggestions cliquables
- Feedback (thumbs up/down)

### 11.2 API Client

```javascript
// dashboard/src/api/index.js

// Envoyer un message
sendChatMessage(message, crypto, sessionId)

// Effacer l'historique
clearChatSession(sessionId)

// Obtenir les suggestions
getChatSuggestions()

// Health check
getChatHealth()

// Envoyer un feedback
sendFeedback(messageId, question, answer, feedbackType, sessionId)
```

---

## 12. Troubleshooting

### Probleme: Reponses vides ou "Je n'ai pas d'information"

**Solutions**:
1. Verifier que Pinecone est indexe: `python scripts/index_documents.py --test`
2. Baisser `RAG_MIN_SCORE` dans `config.py` (actuellement 0.35)
3. Verifier les logs: `tail -f backend/logs/rag.log`

### Probleme: Memoire ne fonctionne pas

**Solutions**:
1. Verifier que `session_id` est envoye depuis le frontend
2. Verifier que la session n'a pas expire (30 min)
3. Tester avec `/api/chat/clear` puis nouvelle conversation

### Probleme: LLM timeout

**Solutions**:
1. Verifier `GROQ_API_KEY` dans `.env`
2. Verifier les quotas Groq
3. Le systeme retourne une erreur gracieuse si LLM indisponible

### Probleme: Questions vagues mal reformulees

**Solutions**:
1. Verifier l'historique de conversation (minimum 1 message precedent)
2. Les questions < 3 mots sont automatiquement reformulees
3. Patterns reconnus: "pourquoi?", "et X?", "lequel?"

---

## 13. Logs

**Fichier**: `backend/logs/rag.log`

**Niveaux**:
- `INFO`: Operations normales
- `WARNING`: Problemes non critiques
- `ERROR`: Erreurs a investiguer

**Exemple**:
```
2024-01-15 10:30:00 - INFO - Chat request: Quel est le sentiment de Bitcoin?
2024-01-15 10:30:00 - INFO - Session user123: 3 messages
2024-01-15 10:30:01 - INFO - Retrieved 5 documents (scores: 0.85, 0.78, 0.72...)
2024-01-15 10:30:02 - INFO - LLM response generated in 0.45s
```

---

## 14. Ressources

| Ressource | Lien |
|-----------|------|
| Pinecone Docs | [docs.pinecone.io](https://docs.pinecone.io/) |
| Groq Console | [console.groq.com](https://console.groq.com/) |
| Sentence Transformers | [sbert.net](https://www.sbert.net/) |
| RAGAS Docs | [docs.ragas.io](https://docs.ragas.io/) |
| LangChain RAG | [langchain.com](https://python.langchain.com/) |
