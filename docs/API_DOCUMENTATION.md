# Documentation API - CryptoVibe

## 1. Vue d'Ensemble

L'API CryptoVibe est construite avec **FastAPI** et expose des endpoints REST pour acceder aux donnees de sentiment crypto, aux analyses statistiques et au chatbot RAG.

### Base URL
```
http://localhost:8000/api
```

### Format des Reponses
Toutes les reponses sont au format **JSON**.

### Codes de Statut
| Code | Description |
|------|-------------|
| 200 | Succes |
| 400 | Requete invalide |
| 404 | Ressource non trouvee |
| 500 | Erreur serveur |

---

## 2. Endpoints Cryptos (`/api/cryptos`)

### 2.1 Liste des Cryptomonnaies

**GET** `/api/cryptos`

Retourne la liste des cryptos avec prix actuels et variation 24h.

**Reponse**:
```json
[
  {
    "symbol": "BTC",
    "name": "Bitcoin",
    "price": 43250.50,
    "change_24h": 2.35,
    "volume_24h": 28500000000
  },
  {
    "symbol": "ETH",
    "name": "Ethereum",
    "price": 2280.75,
    "change_24h": -1.12,
    "volume_24h": 15200000000
  },
  {
    "symbol": "SOL",
    "name": "Solana",
    "price": 98.50,
    "change_24h": 5.67,
    "volume_24h": 2800000000
  }
]
```

---

### 2.2 Details d'une Crypto

**GET** `/api/cryptos/{symbol}`

| Parametre | Type | Description |
|-----------|------|-------------|
| `symbol` | path | Symbole de la crypto (BTC, ETH, SOL) |

**Exemple**: `GET /api/cryptos/BTC`

**Reponse**:
```json
{
  "symbol": "BTC",
  "name": "Bitcoin",
  "price": 43250.50,
  "change_24h": 2.35,
  "volume_24h": 28500000000
}
```

**Erreurs**:
- `404`: Crypto non trouvee

---

### 2.3 Historique des Prix

**GET** `/api/cryptos/{symbol}/chart`

| Parametre | Type | Defaut | Description |
|-----------|------|--------|-------------|
| `symbol` | path | - | Symbole de la crypto |
| `days` | query | 7 | Nombre de jours (1-365) |

**Exemple**: `GET /api/cryptos/BTC/chart?days=30`

**Reponse**:
```json
{
  "symbol": "BTC",
  "days": 30,
  "data": [
    {
      "date": "2024-01-15",
      "price_open": 42500.0,
      "price_close": 43200.0,
      "volume": 28500000000
    },
    {
      "date": "2024-01-16",
      "price_open": 43200.0,
      "price_close": 42800.0,
      "volume": 25600000000
    }
  ]
}
```

---

## 3. Endpoints Sentiment (`/api/sentiment`)

### 3.1 Sentiment Global

**GET** `/api/sentiment/global`

Retourne le sentiment global du marche crypto.

**Reponse**:
```json
{
  "overall_sentiment": 0.12,
  "label": "Legerement Positif",
  "cryptos": {
    "BTC": 0.15,
    "ETH": 0.08,
    "SOL": 0.18
  },
  "total_posts": 27138,
  "period": "30 days"
}
```

---

### 3.2 Timeline Sentiment

**GET** `/api/sentiment/{symbol}/timeline`

| Parametre | Type | Defaut | Description |
|-----------|------|--------|-------------|
| `symbol` | path | - | Symbole de la crypto |
| `days` | query | 30 | Nombre de jours (1-365) |

**Exemple**: `GET /api/sentiment/BTC/timeline?days=7`

**Reponse**:
```json
{
  "symbol": "BTC",
  "current": 0.1523,
  "average": 0.1245,
  "data": [
    {
      "date": "2024-01-15",
      "sentiment_mean": 0.15,
      "sentiment_std": 0.35,
      "positive_count": 145,
      "negative_count": 78,
      "neutral_count": 52,
      "total_count": 275
    }
  ]
}
```

---

## 4. Endpoints Analysis (`/api/analysis`)

### 4.1 Correlation Sentiment-Prix

**GET** `/api/analysis/{symbol}/correlation`

| Parametre | Type | Description |
|-----------|------|-------------|
| `symbol` | path | Symbole de la crypto |

**Exemple**: `GET /api/analysis/BTC/correlation`

**Reponse**:
```json
{
  "crypto": "BTC",
  "pearson_r": -0.0795,
  "p_value": 0.0021,
  "n_observations": 1489,
  "interpretation": "negligible",
  "significant": true
}
```

**Interpretation des valeurs de correlation**:
| Valeur |r| | Label |
|---------|-------|
| >= 0.7 | Forte |
| 0.4 - 0.7 | Moyenne |
| 0.2 - 0.4 | Faible |
| < 0.2 | Negligeable |

---

### 4.2 Analyse de Lag

**GET** `/api/analysis/{symbol}/lag`

Analyse si le sentiment precede les mouvements de prix.

**Exemple**: `GET /api/analysis/BTC/lag`

**Reponse**:
```json
{
  "crypto": "BTC",
  "daily": {
    "pearson_r": -0.045,
    "spearman_r": -0.032,
    "p_value": 0.12,
    "granger_causality": false
  },
  "weekly": {
    "pearson_r": 0.021,
    "spearman_r": 0.018,
    "p_value": 0.45,
    "granger_causality": false
  },
  "monthly": {
    "pearson_r": 0.15,
    "spearman_r": 0.12,
    "p_value": 0.08,
    "granger_causality": false
  }
}
```

---

### 4.3 Statistiques Completes

**GET** `/api/analysis/{symbol}/stats`

Combine correlation et analyse de lag.

**Exemple**: `GET /api/analysis/ETH/stats`

**Reponse**:
```json
{
  "symbol": "ETH",
  "correlation": {
    "pearson_r": -0.045,
    "p_value": 0.2059,
    "n_observations": 1200
  },
  "correlationLabel": "Negligeable",
  "lagAnalysis": {
    "daily": {...},
    "weekly": {...},
    "monthly": {...}
  }
}
```

---

### 4.4 Donnees Scatter Plot

**GET** `/api/analysis/{symbol}/scatter`

| Parametre | Type | Defaut | Description |
|-----------|------|--------|-------------|
| `symbol` | path | - | Symbole de la crypto |
| `days` | query | 30 | Nombre de jours (1-365) |

**Exemple**: `GET /api/analysis/BTC/scatter?days=30`

**Reponse**:
```json
{
  "symbol": "BTC",
  "days": 30,
  "data": [
    {
      "date": "2024-01-15",
      "sentiment": 0.15,
      "price_change": 0.0165
    }
  ]
}
```

---

## 5. Endpoints Events (`/api/events`)

### 5.1 Liste des Posts/Evenements

**GET** `/api/events`

| Parametre | Type | Defaut | Description |
|-----------|------|--------|-------------|
| `crypto` | query | null | Filtre par crypto (BTC, ETH, SOL, ALL) |
| `sentiment` | query | null | Filtre par sentiment (positive, negative, neutral, all) |
| `limit` | query | 50 | Nombre max de resultats (1-500) |

**Exemple**: `GET /api/events?crypto=BTC&sentiment=positive&limit=20`

**Reponse**:
```json
[
  {
    "unified_id": "reddit_abc123",
    "text_content": "Bitcoin looking bullish today! HODL strong.",
    "created_date": "2024-01-15T10:30:00",
    "author": "crypto_trader",
    "source_platform": "reddit",
    "sentiment": "positive",
    "sentiment_score": 0.75,
    "entities": {
      "cryptos": ["BTC"],
      "exchanges": [],
      "influencers": []
    }
  }
]
```

---

### 5.2 Statistiques des Evenements

**GET** `/api/events/stats`

| Parametre | Type | Defaut | Description |
|-----------|------|--------|-------------|
| `crypto` | query | null | Filtre par crypto |

**Exemple**: `GET /api/events/stats?crypto=BTC`

**Reponse**:
```json
{
  "total": 8542,
  "positive": 4125,
  "negative": 2890,
  "neutral": 1527
}
```

---

## 6. Endpoints Chat RAG (`/api/chat`)

### 6.1 Envoyer un Message

**POST** `/api/chat/`

Envoie une question au chatbot RAG avec support de memoire conversationnelle.

**Body**:
```json
{
  "message": "Quel est le sentiment actuel de Bitcoin?",
  "crypto": "BTC",
  "session_id": "user123_session456"
}
```

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `message` | string | Oui | La question a poser |
| `crypto` | string | Non | Filtre optionnel (BTC, ETH, SOL) |
| `session_id` | string | Non | ID pour la memoire conversationnelle |

**Reponse**:
```json
{
  "question": "Quel est le sentiment actuel de Bitcoin?",
  "answer": "Le sentiment actuel de Bitcoin est legerement positif avec un score de 0.15 sur une echelle de -1 a +1...",
  "sources": [
    {
      "id": "doc_123",
      "type": "daily_summary",
      "crypto": "BTC",
      "text": "Resume du sentiment BTC...",
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

---

### 6.2 Effacer l'Historique

**POST** `/api/chat/clear`

Efface l'historique de conversation d'une session.

**Body**:
```json
{
  "session_id": "user123_session456"
}
```

**Reponse**:
```json
{
  "status": "cleared",
  "session_id": "user123_session456"
}
```

---

### 6.3 Suggestions de Questions

**GET** `/api/chat/suggestions`

Retourne 6 questions suggerees aleatoires.

**Reponse**:
```json
{
  "suggestions": [
    "Quel est le sentiment actuel de Bitcoin?",
    "Compare le sentiment de BTC et ETH",
    "Y a-t-il une correlation sentiment-prix?",
    "Quelle crypto a le meilleur sentiment?",
    "Comment fonctionne le score de sentiment?",
    "Que disent les gens sur Solana?"
  ]
}
```

---

### 6.4 Etat de Sante

**GET** `/api/chat/health`

Verifie que tous les composants RAG fonctionnent.

**Reponse**:
```json
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

---

### 6.5 Envoyer un Feedback

**POST** `/api/chat/feedback`

Enregistre un feedback utilisateur (thumbs up/down).

**Body**:
```json
{
  "message_id": "msg_abc123",
  "question": "Quel est le sentiment de Bitcoin?",
  "answer": "Le sentiment est positif...",
  "feedback_type": "positive",
  "session_id": "user123",
  "comment": "Reponse tres utile!"
}
```

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `message_id` | string | Oui | ID unique du message |
| `question` | string | Oui | Question posee |
| `answer` | string | Oui | Reponse du chatbot |
| `feedback_type` | string | Oui | "positive" ou "negative" |
| `session_id` | string | Non | ID de session |
| `comment` | string | Non | Commentaire additionnel |

**Reponse**:
```json
{
  "status": "saved",
  "feedback_id": "fb_xyz789",
  "message": "Feedback enregistre avec succes"
}
```

---

### 6.6 Statistiques des Feedbacks

**GET** `/api/chat/feedback/stats`

Retourne les statistiques des feedbacks.

**Reponse**:
```json
{
  "total": 150,
  "positive": 120,
  "negative": 30,
  "positive_ratio": 0.8,
  "negative_ratio": 0.2
}
```

---

## 7. Documentation OpenAPI

FastAPI genere automatiquement la documentation interactive:

| URL | Description |
|-----|-------------|
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:8000/redoc` | ReDoc |
| `http://localhost:8000/openapi.json` | Schema OpenAPI JSON |

---

## 8. Exemples cURL

### Lister les cryptos
```bash
curl http://localhost:8000/api/cryptos
```

### Obtenir le sentiment de Bitcoin
```bash
curl http://localhost:8000/api/sentiment/BTC/timeline?days=7
```

### Poser une question au chatbot
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Quel est le sentiment de Bitcoin?", "session_id": "test123"}'
```

### Envoyer un feedback
```bash
curl -X POST http://localhost:8000/api/chat/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "msg_001",
    "question": "Test question",
    "answer": "Test answer",
    "feedback_type": "positive"
  }'
```

---

## 9. Configuration CORS

L'API est configuree pour accepter les requetes depuis:
- `http://localhost:3000` (Dashboard React)

Pour modifier, editer `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 10. Lancer l'API

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

L'API sera accessible sur `http://localhost:8000`.
