"""
Dataset de test pour l'evaluation RAGAS du chatbot crypto.

Ce module charge le dataset depuis le fichier JSON externe test_dataset.json
pour faciliter la modification et la visualisation des questions de test.

Categories de questions:
1. sentiment_general - Questions sur le sentiment (BTC, ETH, SOL)
2. comparison - Comparaisons entre cryptos
3. correlation - Questions sur correlation sentiment-prix
4. temporal - Analyse temporelle du sentiment
5. detailed - Analyses completes
6. vague - Questions vagues (test reformulation)
7. faq - Questions frequentes

Usage:
    from app.rag.evaluation.test_dataset import TEST_DATASET, get_test_samples

    # Tous les samples
    samples = TEST_DATASET

    # Sous-ensemble aleatoire
    samples = get_test_samples(10)

    # Par categorie
    samples = get_test_samples(n=5, category="comparison")
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Optional

from app.rag.logger import get_logger

logger = get_logger("test_dataset")

# =====================================================================
# CHARGEMENT DU DATASET DEPUIS JSON
# =====================================================================

def _load_dataset() -> Dict:
    """Charge le dataset depuis le fichier JSON"""
    json_path = Path(__file__).parent / "test_dataset.json"

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Dataset charge: {len(data.get('questions', []))} questions")
        return data
    except FileNotFoundError:
        logger.error(f"Fichier non trouve: {json_path}")
        return {"questions": [], "quick_eval_samples": [], "metadata": {}}
    except json.JSONDecodeError as e:
        logger.error(f"Erreur JSON: {e}")
        return {"questions": [], "quick_eval_samples": [], "metadata": {}}


# Charger le dataset au demarrage
_DATASET = _load_dataset()

# Export des donnees
TEST_DATASET: List[Dict] = _DATASET.get("questions", [])
QUICK_EVAL_SAMPLES: List[Dict] = _DATASET.get("quick_eval_samples", [])
DATASET_METADATA: Dict = _DATASET.get("metadata", {})


# =====================================================================
# FONCTIONS UTILITAIRES
# =====================================================================

def reload_dataset() -> None:
    """Recharge le dataset depuis le fichier JSON"""
    global _DATASET, TEST_DATASET, QUICK_EVAL_SAMPLES, DATASET_METADATA

    _DATASET = _load_dataset()
    TEST_DATASET = _DATASET.get("questions", [])
    QUICK_EVAL_SAMPLES = _DATASET.get("quick_eval_samples", [])
    DATASET_METADATA = _DATASET.get("metadata", {})

    logger.info("Dataset recharge")


def get_test_samples(
    n: Optional[int] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    shuffle: bool = True
) -> List[Dict]:
    """
    Retourne un sous-ensemble du dataset de test.

    Args:
        n: Nombre de samples (None = tous)
        category: Filtrer par categorie (sentiment_general, comparison, etc.)
        difficulty: Filtrer par difficulte (easy, medium, hard)
        shuffle: Melanger les samples

    Returns:
        Liste de samples
    """
    samples = TEST_DATASET.copy()

    # Filtrer par categorie
    if category:
        samples = [s for s in samples if s.get("category") == category]
        logger.debug(f"Filtre categorie '{category}': {len(samples)} samples")

    # Filtrer par difficulte
    if difficulty:
        samples = [s for s in samples if s.get("difficulty") == difficulty]
        logger.debug(f"Filtre difficulte '{difficulty}': {len(samples)} samples")

    # Melanger
    if shuffle:
        random.shuffle(samples)

    # Limiter
    if n is not None:
        samples = samples[:n]

    return samples


def get_samples_by_difficulty(difficulty: str) -> List[Dict]:
    """
    Retourne les samples par niveau de difficulte.

    Args:
        difficulty: "easy", "medium", ou "hard"

    Returns:
        Liste de samples
    """
    return [s for s in TEST_DATASET if s.get("difficulty") == difficulty]


def get_samples_by_category(category: str) -> List[Dict]:
    """
    Retourne les samples par categorie.

    Args:
        category: Nom de la categorie

    Returns:
        Liste de samples
    """
    return [s for s in TEST_DATASET if s.get("category") == category]


def get_categories() -> List[str]:
    """Retourne la liste des categories disponibles"""
    return DATASET_METADATA.get("categories", list(set(
        s.get("category", "other") for s in TEST_DATASET
    )))


def get_difficulties() -> List[str]:
    """Retourne la liste des niveaux de difficulte"""
    return DATASET_METADATA.get("difficulties", ["easy", "medium", "hard"])


def get_dataset_stats() -> Dict:
    """Retourne les statistiques du dataset"""
    categories = {}
    difficulties = {}

    for sample in TEST_DATASET:
        cat = sample.get("category", "other")
        diff = sample.get("difficulty", "unknown")

        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1

    return {
        "total_samples": len(TEST_DATASET),
        "categories": categories,
        "difficulties": difficulties,
        "metadata": DATASET_METADATA
    }


def get_question_by_id(question_id: int) -> Optional[Dict]:
    """
    Retourne une question par son ID.

    Args:
        question_id: ID de la question

    Returns:
        Question ou None si non trouvee
    """
    for q in TEST_DATASET:
        if q.get("id") == question_id:
            return q
    return None


def get_vague_questions() -> List[Dict]:
    """Retourne les questions vagues (pour tester la reformulation)"""
    return [s for s in TEST_DATASET if s.get("requires_context", False)]


# =====================================================================
# MAIN - Affichage des stats
# =====================================================================

if __name__ == "__main__":
    # Afficher les stats du dataset
    stats = get_dataset_stats()

    print("=" * 50)
    print("RAGAS TEST DATASET - STATISTICS")
    print("=" * 50)
    print(f"Total questions: {stats['total_samples']}")
    print()
    print("Categories:")
    for cat, count in stats["categories"].items():
        print(f"  - {cat}: {count}")
    print()
    print("Difficulties:")
    for diff, count in stats["difficulties"].items():
        print(f"  - {diff}: {count}")
    print()
    print("Quick eval samples:", len(QUICK_EVAL_SAMPLES))
    print("=" * 50)
