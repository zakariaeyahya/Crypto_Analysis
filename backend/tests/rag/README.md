# Tests RAG - Documentation

## Structure des tests

```
backend/tests/rag/
├── README.md                 # Ce fichier
├── run_all_tests.sh          # Exécute tous les tests
│
├── test_config.py            # Test configuration
├── test_config.sh
│
├── test_document_loader.py   # Test chargement documents
├── test_document_loader.sh
│
├── test_chunker.py           # Test découpage chunks
├── test_chunker.sh
│
├── test_embedding.py         # Test service embedding
├── test_embedding.sh
│
├── test_pinecone.py          # Test service Pinecone
├── test_pinecone.sh
│
├── test_retriever.py         # Test service retrieval
├── test_retriever.sh
│
├── test_llm.py               # Test service LLM
├── test_llm.sh
│
├── test_rag_service.py       # Test pipeline RAG complet
├── test_rag_service.sh
│
├── test_api_chat.py          # Test endpoints API
└── test_api_chat.sh
```

## Prérequis

1. **Variables d'environnement** (`.env` dans `backend/`):
```bash
PINECONE_API_KEY=pcsk_xxx...
PINECONE_INDEX_NAME=crypto-sentiment-rag
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxx...
```

2. **Dépendances Python**:
```bash
pip install -r requirements.txt
```

3. **Index Pinecone** (pour tests Pinecone/Retriever/RAG):
```bash
python scripts/index_documents.py --clear --test
```

## Exécution des tests

### Tous les tests
```bash
cd backend
bash tests/rag/run_all_tests.sh
```

### Tests individuels
```bash
cd backend

# Configuration
bash tests/rag/test_config.sh
# ou
python tests/rag/test_config.py

# Document Loader
bash tests/rag/test_document_loader.sh

# Chunker
bash tests/rag/test_chunker.sh

# Embedding
bash tests/rag/test_embedding.sh

# Pinecone
bash tests/rag/test_pinecone.sh

# Retriever
bash tests/rag/test_retriever.sh

# LLM
bash tests/rag/test_llm.sh

# RAG Service
bash tests/rag/test_rag_service.sh

# API Chat (nécessite serveur lancé)
bash tests/rag/test_api_chat.sh
```

### Test API (serveur requis)

1. Lancer le serveur:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. Dans un autre terminal:
```bash
cd backend
bash tests/rag/test_api_chat.sh
```

## Description des tests

### test_config
- Vérifie les variables d'environnement
- Vérifie les chemins des fichiers de données
- Vérifie le mapping des cryptos

### test_document_loader
- `load_posts()` - Posts Twitter/Reddit
- `load_timeseries()` - Résumés quotidiens
- `load_correlations()` - Analyses de corrélation
- `load_lag_analysis()` - Analyses de lag
- `load_prices()` - Prix historiques
- `load_faq()` - FAQ statiques
- `load_all()` - Tous les documents

### test_chunker
- Découpage de documents courts
- Découpage de documents longs
- Statistiques des chunks
- Vérification taille maximale

### test_embedding
- Initialisation du modèle
- `embed_text()` - Texte simple
- `embed_texts_batch()` - Batch de textes
- `embed_chunks()` - Chunks avec métadonnées
- Vérification similarité sémantique

### test_pinecone
- Connexion à Pinecone
- `get_stats()` - Statistiques index
- `search()` - Recherche vectorielle
- `search()` avec filtre crypto

### test_retriever
- `extract_crypto_from_query()` - Détection crypto
- `build_filter()` - Construction filtres
- `retrieve()` - Recherche documents
- `retrieve_with_context()` - Contexte formaté
- `retrieve_by_types()` - Recherche par type

### test_llm
- Vérification configuration
- `is_available()` - Disponibilité
- `generate()` - Génération simple
- `generate()` avec system prompt
- `generate_with_context()` - Avec contexte

### test_rag_service
- `health_check()` - Santé du système
- `process_query()` - Pipeline complet
- `get_quick_answer()` - Réponse rapide
- `get_crypto_summary()` - Résumé crypto
- `compare_cryptos()` - Comparaison
- Vérification des sources

### test_api_chat
- `GET /api/chat/health` - Santé
- `GET /api/chat/suggestions` - Suggestions
- `POST /api/chat/` - Chat simple
- `POST /api/chat/` - Avec filtre crypto
- Validation message vide
- Vérification sources

## Résultats attendus

```
==========================================
  RESUME FINAL
==========================================

  Tests passés: 8 / 8
  Tests échoués: 0 / 8

  ✓ TOUS LES TESTS SONT PASSES!
```

## Dépannage

### PINECONE_API_KEY non défini
```
Créez le fichier backend/.env avec:
PINECONE_API_KEY=pcsk_xxx...
```

### Index Pinecone vide
```
Exécutez l'indexation:
python scripts/index_documents.py --clear
```

### LLM non disponible
```
Vérifiez GROQ_API_KEY dans .env
ou changez LLM_PROVIDER=ollama (local)
```

### Serveur non lancé (test API)
```
Lancez: uvicorn app.main:app --reload --port 8000
```
