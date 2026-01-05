# Guide d'Installation - CryptoVibe

## 1. Prerequis

### 1.1 Logiciels Requis

| Logiciel | Version | Verification |
|----------|---------|--------------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | 2.0+ | `git --version` |

### 1.2 Comptes et API Keys

| Service | Usage | Lien |
|---------|-------|------|
| **Pinecone** | Base vectorielle RAG | [pinecone.io](https://www.pinecone.io/) |
| **Groq** | LLM (Llama 3.3 70B) | [console.groq.com](https://console.groq.com/) |
| **Reddit** (optionnel) | Scraping posts | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) |

---

## 2. Installation

### 2.1 Cloner le Projet

```bash
git clone https://github.com/votre-repo/Crypto_Analysis.git
cd Crypto_Analysis
```

### 2.2 Structure du Projet

```
Crypto_Analysis/
├── backend/          # API FastAPI + RAG
├── dashboard/        # Frontend React
├── data/             # Donnees Bronze/Silver/Gold
├── docs/             # Documentation
└── ...
```

---

## 3. Configuration Backend

### 3.1 Environnement Virtuel Python

```bash
cd backend

# Creer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3.2 Installer les Dependances

```bash
pip install -r requirements.txt
```

**Dependances principales:**
| Package | Version | Usage |
|---------|---------|-------|
| fastapi | 0.109.0 | API REST |
| uvicorn | 0.27.0 | Serveur ASGI |
| pydantic | 2.5.3 | Validation |
| sentence-transformers | 2.2.0+ | Embeddings |
| pinecone | 3.0.0+ | Base vectorielle |
| groq | 0.4.0+ | LLM |
| ragas | 0.2.0+ | Evaluation (optionnel) |

### 3.3 Configuration des Variables d'Environnement

Creer le fichier `backend/.env`:

```bash
# backend/.env

# === PINECONE (Obligatoire pour RAG) ===
PINECONE_API_KEY=pcsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PINECONE_INDEX_NAME=crypto-sentiment-rag

# === LLM (Obligatoire pour RAG) ===
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# === REDDIT (Optionnel - pour scraping) ===
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=CryptoVibe/1.0
```

### 3.4 Obtenir les API Keys

#### Pinecone
1. Creer un compte sur [pinecone.io](https://www.pinecone.io/)
2. Creer un index:
   - **Name**: `crypto-sentiment-rag`
   - **Dimensions**: `384`
   - **Metric**: `cosine`
3. Copier l'API Key depuis le dashboard

#### Groq
1. Creer un compte sur [console.groq.com](https://console.groq.com/)
2. Generer une API Key
3. Copier la cle (commence par `gsk_`)

### 3.5 Indexer les Documents (RAG)

```bash
cd backend

# Indexer tous les documents dans Pinecone
python scripts/index_documents.py --clear

# Verifier l'indexation
python scripts/index_documents.py --test
```

**Resultat attendu:**
```
Index stats: ~26,000 vectors
Types: posts, daily_summary, analysis, price, faq
```

---

## 4. Configuration Frontend

### 4.1 Installer les Dependances

```bash
cd dashboard
npm install
```

**Dependances principales:**
| Package | Version | Usage |
|---------|---------|-------|
| react | 18.2.0 | Framework UI |
| react-router-dom | 6.20.0 | Navigation |
| recharts | 2.10.0 | Graphiques |
| lucide-react | 0.562.0 | Icones |

### 4.2 Configuration API

Le frontend est configure pour se connecter a `http://localhost:8000/api`.

Pour modifier, editer `dashboard/src/api/index.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

---

## 5. Lancer l'Application

### 5.1 Demarrer le Backend

```bash
cd backend

# Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Lancer le serveur
uvicorn app.main:app --reload --port 8000
```

**Verification:**
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/api/chat/health

### 5.2 Demarrer le Frontend

```bash
cd dashboard
npm start
```

**Verification:**
- Dashboard: http://localhost:3000

### 5.3 Commande Rapide (2 terminaux)

**Terminal 1 - Backend:**
```bash
cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd dashboard && npm start
```

---

## 6. Verification de l'Installation

### 6.1 Tester l'API

```bash
# Liste des cryptos
curl http://localhost:8000/api/cryptos

# Sentiment global
curl http://localhost:8000/api/sentiment/global

# Health check RAG
curl http://localhost:8000/api/chat/health
```

### 6.2 Tester le Chatbot

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Quel est le sentiment de Bitcoin?"}'
```

### 6.3 Tester le Frontend

1. Ouvrir http://localhost:3000
2. Naviguer vers les differentes pages (Overview, Timeline, Analysis)
3. Tester le chatbot (icone en bas a droite)

---

## 7. Scripts Utiles

### 7.1 Backend

```bash
cd backend

# Lancer les tests RAG
bash tests/rag/run_all_tests.sh

# Evaluation RAGAS rapide
python scripts/evaluate_rag.py --quick

# Reindexer Pinecone
python scripts/index_documents.py --clear
```

### 7.2 Data Pipeline

```bash
# Recuperer les prix crypto
python fetch_crypto_data/fetch_crypto_data_yfinance.py

# Nettoyer les donnees
python data_cleaning/clean_data.py

# Analyse de correlation
python analysis/correlation.py
```

### 7.3 Frontend

```bash
cd dashboard

# Lancer en dev
npm start

# Build production
npm run build

# Tests
npm test
```

---

## 8. Troubleshooting

### 8.1 Erreurs Courantes

#### "PINECONE_API_KEY not found"
```bash
# Verifier que le fichier .env existe
cat backend/.env

# Verifier que la variable est chargee
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('PINECONE_API_KEY'))"
```

#### "ModuleNotFoundError"
```bash
# Verifier l'environnement virtuel
which python  # Linux/Mac
where python  # Windows

# Reinstaller les dependances
pip install -r requirements.txt
```

#### "CORS Error" dans le navigateur
Verifier que le backend est lance sur le port 8000:
```bash
curl http://localhost:8000/api/cryptos
```

#### "Empty search results" (RAG)
```bash
# Reindexer les documents
cd backend
python scripts/index_documents.py --clear --test
```

#### Erreur Unicode (Windows)
```bash
# Ajouter avant les commandes Python
set PYTHONIOENCODING=utf-8
```

### 8.2 Logs

**Backend logs:**
```bash
tail -f backend/logs/rag.log
```

**Uvicorn logs:**
Les logs s'affichent dans le terminal ou le backend est lance.

---

## 9. Configuration Avancee

### 9.1 Changer le LLM

Dans `backend/.env`:
```bash
# Utiliser Ollama (local)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1

# Utiliser Groq (cloud)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxx
```

### 9.2 Ajuster les Parametres RAG

Dans `backend/app/rag/config.py`:
```python
RAG_TOP_K = 5           # Nombre de documents recuperes
RAG_MIN_SCORE = 0.35    # Score minimum de similarite
```

### 9.3 Configurer Airflow (Optionnel)

Pour l'orchestration automatique du pipeline:
```bash
cd docker
docker-compose up -d
```

---

## 10. Mise a Jour

### 10.1 Mettre a Jour le Code

```bash
git pull origin main
```

### 10.2 Mettre a Jour les Dependances

**Backend:**
```bash
cd backend
pip install -r requirements.txt --upgrade
```

**Frontend:**
```bash
cd dashboard
npm update
```

### 10.3 Reindexer apres Mise a Jour des Donnees

```bash
cd backend
python scripts/index_documents.py --clear
```

---

## 11. Ressources

| Ressource | Lien |
|-----------|------|
| Documentation FastAPI | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| Documentation React | [react.dev](https://react.dev/) |
| Pinecone Docs | [docs.pinecone.io](https://docs.pinecone.io/) |
| Groq Console | [console.groq.com](https://console.groq.com/) |
| RAGAS Docs | [docs.ragas.io](https://docs.ragas.io/) |

---

## 12. Checklist d'Installation

- [ ] Python 3.10+ installe
- [ ] Node.js 18+ installe
- [ ] Projet clone
- [ ] Environnement virtuel Python cree
- [ ] Dependances backend installees
- [ ] Fichier `.env` configure
- [ ] API Key Pinecone obtenue
- [ ] API Key Groq obtenue
- [ ] Index Pinecone cree (384 dimensions)
- [ ] Documents indexes
- [ ] Dependances frontend installees
- [ ] Backend demarre (port 8000)
- [ ] Frontend demarre (port 3000)
- [ ] Test API reussi
- [ ] Test chatbot reussi
