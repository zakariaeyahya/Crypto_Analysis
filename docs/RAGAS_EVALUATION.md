# Documentation RAGAS - Evaluation du Systeme RAG CryptoVibe

## 1. Introduction

RAGAS (Retrieval Augmented Generation Assessment) est un framework d'evaluation utilise pour mesurer la qualite du systeme de chatbot RAG de CryptoVibe. Cette documentation detaille l'architecture, les metriques et l'utilisation du module d'evaluation.

## 2. Architecture du Module

```
backend/app/rag/evaluation/
├── __init__.py
├── ragas_evaluator.py    # Evaluateurs RAGAS et Simple
└── test_dataset.py       # Dataset de 26 questions de test

backend/scripts/
└── evaluate_rag.py       # Script CLI d'evaluation

backend/evaluation_results/
└── ragas_eval_*.json     # Resultats sauvegardes
```

## 3. Composants Principaux

### 3.1 RAGASEvaluator

Classe principale pour l'evaluation avec le framework RAGAS.

```python
from app.rag.evaluation import RAGASEvaluator

evaluator = RAGASEvaluator()
results = evaluator.evaluate_dataset(test_samples)
```

**Fonctionnalites:**
- Evaluation avec metriques RAGAS officielles
- Integration avec Groq LLM (Llama 3.3 70B)
- Sauvegarde automatique des resultats en JSON
- Support evaluation single ou batch

### 3.2 SimpleEvaluator

Evaluateur de fallback utilisant des heuristiques (sans dependance RAGAS).

```python
from app.rag.evaluation.ragas_evaluator import SimpleEvaluator

evaluator = SimpleEvaluator()
scores = evaluator.evaluate_response(question, answer, contexts)
```

**Heuristiques utilisees:**
| Metrique | Description | Calcul |
|----------|-------------|--------|
| `response_length` | Longueur de reponse | `min(1.0, len(words) / 100)` |
| `context_coverage` | Mots du contexte dans la reponse | Intersection des vocabulaires |
| `question_relevance` | Mots de la question dans la reponse | Coverage × 3 |
| `crypto_mention` | Presence de cryptos (BTC, ETH, SOL) | 1.0 si present, 0.5 sinon |

## 4. Metriques RAGAS

### 4.1 Faithfulness (Fidelite)
Mesure si la reponse est fidele aux documents recuperes.
- **Score eleve**: La reponse ne contient que des informations presentes dans les contextes
- **Score faible**: La reponse hallucine ou invente des informations

### 4.2 Answer Relevancy (Pertinence)
Evalue la pertinence de la reponse par rapport a la question posee.
- **Score eleve**: La reponse repond directement a la question
- **Score faible**: La reponse est hors sujet

### 4.3 Context Precision (Precision du Contexte)
Verifie si les documents recuperes par Pinecone sont pertinents.
- **Score eleve**: Tous les documents recuperes sont utiles
- **Score faible**: Documents non pertinents recuperes

## 5. Dataset de Test

### 5.1 Structure
Le dataset contient **26 questions** reparties en **7 categories**:

| Categorie | Nombre | Description |
|-----------|--------|-------------|
| `sentiment_general` | 5 | Questions sur le sentiment (BTC, ETH, SOL) |
| `comparison` | 4 | Comparaisons entre cryptos |
| `correlation` | 4 | Questions sur correlation sentiment-prix |
| `temporal` | 3 | Evolution temporelle du sentiment |
| `detailed` | 3 | Analyses completes |
| `vague` | 4 | Questions vagues (test reformulation) |
| `faq` | 3 | Questions frequentes |

### 5.2 Niveaux de Difficulte

| Niveau | Nombre | Exemples |
|--------|--------|----------|
| `easy` | 11 | "Quel est le sentiment de Bitcoin?" |
| `medium` | 10 | "Compare le sentiment de BTC et ETH" |
| `hard` | 5 | "Quelle crypto a la plus forte correlation?" |

### 5.3 Format d'une Question

```python
{
    "question": "Quel est le sentiment actuel de Bitcoin?",
    "expected_topics": ["sentiment", "bitcoin", "score"],
    "category": "sentiment_general",
    "difficulty": "easy",
    "ground_truth": "Le sentiment de Bitcoin doit inclure un score numerique..."
}
```

## 6. Utilisation

### 6.1 Commandes CLI

```bash
cd backend

# Evaluation rapide (5 samples, heuristiques)
python scripts/evaluate_rag.py --quick

# Evaluation complete avec RAGAS
python scripts/evaluate_rag.py --full

# Nombre de samples specifique
python scripts/evaluate_rag.py --samples 10

# Par categorie
python scripts/evaluate_rag.py --category comparison

# Mode simple (heuristiques seulement)
python scripts/evaluate_rag.py --simple

# Tester une seule question
python scripts/evaluate_rag.py --query "Quel est le sentiment de Bitcoin?"

# Statistiques du dataset
python scripts/evaluate_rag.py --stats
```

### 6.2 Utilisation Programmatique

```python
from app.rag.evaluation import RAGASEvaluator
from app.rag.evaluation.test_dataset import get_test_samples

# Initialiser l'evaluateur
evaluator = RAGASEvaluator()

# Obtenir des samples
samples = get_test_samples(n=10, category="comparison")

# Evaluer
results = evaluator.evaluate_dataset(
    samples,
    run_rag=True,       # Executer le pipeline RAG
    save_results=True   # Sauvegarder en JSON
)

# Afficher le resume
evaluator.log_summary(results)
```

### 6.3 Evaluation d'une Seule Question

```python
from app.rag.rag_service import get_rag_service

rag = get_rag_service()
result = rag.process_query("Quel est le sentiment de Bitcoin?")

# Evaluer avec RAGAS
scores = evaluator.evaluate_from_rag_result(result)
print(scores)
# {'faithfulness': 0.85, 'answer_relevancy': 0.78, 'context_precision': 0.72}
```

## 7. Format des Resultats

### 7.1 Structure JSON

```json
{
    "timestamp": "2024-01-15T10:30:00",
    "num_samples": 10,
    "num_evaluated": 10,
    "summary": {
        "faithfulness": {
            "mean": 0.74,
            "min": 0.65,
            "max": 0.89,
            "count": 10
        },
        "answer_relevancy": {
            "mean": 0.71,
            "min": 0.58,
            "max": 0.85,
            "count": 10
        },
        "context_precision": {
            "mean": 0.72,
            "min": 0.60,
            "max": 0.88,
            "count": 10
        },
        "overall": 0.721
    },
    "results": [
        {
            "question": "Quel est le sentiment actuel de Bitcoin?",
            "answer": "Le sentiment de Bitcoin est actuellement positif...",
            "num_contexts": 5,
            "ground_truth": "...",
            "scores": {
                "faithfulness": 0.85,
                "answer_relevancy": 0.78,
                "context_precision": 0.72
            }
        }
    ]
}
```

### 7.2 Interpretation des Scores

| Score | Interpretation | Action |
|-------|----------------|--------|
| >= 0.80 | Excellent | Systeme performant |
| 0.60 - 0.79 | Bon | Ameliorations mineures possibles |
| 0.40 - 0.59 | Moyen | Revoir le pipeline RAG |
| < 0.40 | Faible | Probleme majeur a corriger |

## 8. Resultats Typiques CryptoVibe

### 8.1 Scores Moyens

| Metrique | Score | Interpretation |
|----------|-------|----------------|
| Faithfulness | 0.74 | Bon - reponses fideles aux sources |
| Answer Relevancy | 0.71 | Bon - reponses pertinentes |
| Context Precision | 0.72 | Bon - documents recuperes pertinents |
| **Score Global** | **0.721** | **Bon (72.1%)** |

### 8.2 Performance par Categorie

| Categorie | Score | Observations |
|-----------|-------|--------------|
| Correlations | 76.4% | Meilleure performance |
| Comparaisons | 77.5% | Synthese multi-sources efficace |
| Sentiment actuel | 69.3% | Donnees temporelles complexes |
| FAQ | 71.9% | Reponses pedagogiques |

## 9. Configuration

### 9.1 Variables d'Environnement

```bash
# backend/.env
GROQ_API_KEY=gsk_xxx...          # Requis pour RAGAS
PINECONE_API_KEY=pcsk_xxx...     # Requis pour RAG
```

### 9.2 Installation RAGAS

```bash
pip install ragas datasets
```

Si RAGAS n'est pas disponible, le `SimpleEvaluator` est utilise automatiquement comme fallback.

## 10. Bonnes Pratiques

### 10.1 Evaluation Reguliere
- Executer `--quick` apres chaque modification du RAG
- Executer `--full` avant chaque release

### 10.2 Analyse des Erreurs
- Verifier les questions avec scores < 0.5
- Identifier les patterns d'echec (ironie, questions vagues)

### 10.3 Amelioration Continue
- Ajouter des questions au dataset pour couvrir les cas d'echec
- Ajuster les prompts du RAG selon les resultats
- Reindexer Pinecone si context_precision est faible

## 11. Troubleshooting

### Erreur: RAGAS non disponible
```bash
pip install ragas datasets
```

### Erreur: GROQ_API_KEY non configure
Verifier le fichier `backend/.env` contient la cle API Groq.

### Scores tres bas
1. Verifier que Pinecone est correctement indexe
2. Verifier le min_score dans `config.py` (actuellement 0.35)
3. Reindexer: `python scripts/index_documents.py --clear`

### Timeout lors de l'evaluation
Reduire le nombre de samples: `--samples 5`

## 12. References

- [RAGAS Documentation](https://docs.ragas.io/)
- [Groq API](https://console.groq.com/)
- [Pinecone Documentation](https://docs.pinecone.io/)
