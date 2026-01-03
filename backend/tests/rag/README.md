# Tests RAG - Documentation

## Evaluation RAGAS

Les tests du systeme RAG utilisent maintenant le module d'evaluation RAGAS.

### Structure

```
backend/
├── app/rag/evaluation/           # Module d'evaluation
│   ├── __init__.py
│   ├── ragas_evaluator.py        # RAGASEvaluator + SimpleEvaluator
│   └── test_dataset.py           # 26 questions de test
├── scripts/
│   ├── evaluate_rag.py           # Script d'evaluation
│   ├── run_evaluation.sh         # Script bash
│   └── run_evaluation.bat        # Script Windows
└── evaluation_results/           # Resultats JSON
```

## Prerequis

1. **Variables d'environnement** (`.env` dans `backend/`):
```bash
PINECONE_API_KEY=pcsk_xxx...
PINECONE_INDEX_NAME=crypto-sentiment-rag
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxx...
```

2. **Dependances Python**:
```bash
pip install -r requirements.txt
```

3. **Index Pinecone** (si pas encore indexe):
```bash
python scripts/index_documents.py --clear --test
```

## Execution des tests

### Evaluation rapide (5 samples)
```bash
cd backend
python scripts/evaluate_rag.py --quick
```

### Tester une question specifique
```bash
python scripts/evaluate_rag.py --query "Quel est le sentiment de Bitcoin?"
```

### Statistiques du dataset
```bash
python scripts/evaluate_rag.py --stats
```

### Evaluation par categorie
```bash
python scripts/evaluate_rag.py --category comparison --samples 5
python scripts/evaluate_rag.py --category correlation --samples 5
python scripts/evaluate_rag.py --category sentiment_general --samples 5
```

### Evaluation complete RAGAS
```bash
# Installer RAGAS d'abord
pip install ragas datasets

# Lancer l'evaluation
python scripts/evaluate_rag.py --full --samples 20
```

## Categories de test

| Categorie | Description | Samples |
|-----------|-------------|---------|
| sentiment_general | Sentiment d'une crypto | 5 |
| comparison | Comparaison entre cryptos | 4 |
| correlation | Correlation sentiment/prix | 4 |
| temporal | Evolution temporelle | 3 |
| detailed | Analyses detaillees | 3 |
| vague | Questions vagues (reformulation) | 4 |
| faq | Questions frequentes | 3 |

## Metriques

### Mode Simple (Heuristiques)
- `response_length` - Longueur de la reponse
- `context_coverage` - Couverture du contexte
- `question_relevance` - Pertinence a la question
- `crypto_mention` - Mention des cryptos
- `overall` - Score global

### Mode RAGAS (si installe)
- `faithfulness` - Fidelite aux documents
- `answer_relevancy` - Pertinence de la reponse
- `context_precision` - Precision du contexte

## Resultats attendus

```
Score moyen: 0.716 (71.6%)

Details par question:
------------------------------------------------------------
  Quel est le sentiment actuel de Bitcoin?      | 0.704
  Compare le sentiment de Bitcoin et Ether...   | 0.672
  Y a-t-il une correlation entre sentiment...   | 0.708
  Quelle crypto a le meilleur sentiment?        | 0.748
  Comment fonctionne le score de sentiment...   | 0.750
```

## Logs

Les logs sont sauvegardes dans:
```
backend/logs/rag.log
```

Les resultats d'evaluation sont sauvegardes dans:
```
backend/evaluation_results/ragas_eval_YYYYMMDD_HHMMSS.json
```

## Depannage

### PINECONE_API_KEY non defini
```
Creez le fichier backend/.env avec:
PINECONE_API_KEY=pcsk_xxx...
```

### Index Pinecone vide
```
Executez l'indexation:
python scripts/index_documents.py --clear
```

### LLM non disponible
```
Verifiez GROQ_API_KEY dans .env
```

### RAGAS non installe
```
pip install ragas datasets
Le mode simple (heuristiques) sera utilise par defaut.
```
