"""
Dataset de test pour l'evaluation RAGAS du chatbot crypto.

Ce dataset contient des questions types avec les reponses attendues
pour mesurer la qualite du systeme RAG.

Categories de questions:
1. Sentiment general
2. Comparaison de cryptos
3. Correlation prix/sentiment
4. Analyse temporelle
5. Questions vagues (reformulation)

Usage:
    from app.rag.evaluation.test_dataset import TEST_DATASET, get_test_samples

    # Tous les samples
    samples = TEST_DATASET

    # Sous-ensemble aleatoire
    samples = get_test_samples(10)
"""

import random
from typing import List, Dict

from app.rag.logger import get_logger

logger = get_logger("test_dataset")

# =====================================================================
# DATASET COMPLET
# =====================================================================

TEST_DATASET: List[Dict] = [
    # ===================================================================
    # CATEGORIE 1: SENTIMENT GENERAL
    # ===================================================================
    {
        "question": "Quel est le sentiment actuel de Bitcoin?",
        "expected_topics": ["sentiment", "bitcoin", "score"],
        "category": "sentiment_general",
        "difficulty": "easy",
        "ground_truth": "Le sentiment de Bitcoin doit inclure un score numerique et une interpretation (positif/negatif/neutre)."
    },
    {
        "question": "Comment se porte le sentiment d'Ethereum?",
        "expected_topics": ["sentiment", "ethereum", "tendance"],
        "category": "sentiment_general",
        "difficulty": "easy",
        "ground_truth": "Le sentiment d'Ethereum avec score et interpretation."
    },
    {
        "question": "Parle-moi du sentiment de Solana",
        "expected_topics": ["sentiment", "solana"],
        "category": "sentiment_general",
        "difficulty": "easy",
        "ground_truth": "Analyse du sentiment Solana avec donnees chiffrees."
    },
    {
        "question": "Le sentiment crypto est-il positif ou negatif en ce moment?",
        "expected_topics": ["sentiment", "global", "marche"],
        "category": "sentiment_general",
        "difficulty": "medium",
        "ground_truth": "Vue d'ensemble du sentiment du marche crypto avec les 3 cryptos."
    },
    {
        "question": "Quelle est l'ambiance generale sur les reseaux sociaux pour les cryptos?",
        "expected_topics": ["sentiment", "social", "global"],
        "category": "sentiment_general",
        "difficulty": "medium",
        "ground_truth": "Analyse du sentiment social global."
    },

    # ===================================================================
    # CATEGORIE 2: COMPARAISON
    # ===================================================================
    {
        "question": "Compare le sentiment de Bitcoin et Ethereum",
        "expected_topics": ["bitcoin", "ethereum", "comparaison", "sentiment"],
        "category": "comparison",
        "difficulty": "medium",
        "ground_truth": "Comparaison directe des scores de sentiment BTC vs ETH avec interpretation."
    },
    {
        "question": "Quelle crypto a le meilleur sentiment actuellement?",
        "expected_topics": ["meilleur", "sentiment", "crypto"],
        "category": "comparison",
        "difficulty": "medium",
        "ground_truth": "Classement des 3 cryptos par score de sentiment avec le gagnant."
    },
    {
        "question": "Entre BTC, ETH et SOL, lequel est le plus apprecie?",
        "expected_topics": ["btc", "eth", "sol", "appreciation"],
        "category": "comparison",
        "difficulty": "medium",
        "ground_truth": "Comparaison des 3 cryptos avec scores."
    },
    {
        "question": "Compare le sentiment de toutes les cryptos",
        "expected_topics": ["comparaison", "toutes", "sentiment"],
        "category": "comparison",
        "difficulty": "hard",
        "ground_truth": "Tableau comparatif complet des 3 cryptos."
    },

    # ===================================================================
    # CATEGORIE 3: CORRELATION PRIX/SENTIMENT
    # ===================================================================
    {
        "question": "Y a-t-il une correlation entre le sentiment et le prix de Bitcoin?",
        "expected_topics": ["correlation", "prix", "bitcoin", "pearson"],
        "category": "correlation",
        "difficulty": "hard",
        "ground_truth": "Coefficient de correlation de Pearson avec interpretation."
    },
    {
        "question": "Le sentiment influence-t-il le prix d'Ethereum?",
        "expected_topics": ["influence", "prix", "ethereum", "sentiment"],
        "category": "correlation",
        "difficulty": "hard",
        "ground_truth": "Analyse de la correlation sentiment-prix pour ETH."
    },
    {
        "question": "Quelle crypto a la plus forte correlation sentiment-prix?",
        "expected_topics": ["correlation", "forte", "crypto"],
        "category": "correlation",
        "difficulty": "hard",
        "ground_truth": "Comparaison des correlations avec la crypto gagnante."
    },
    {
        "question": "Explique-moi la relation entre sentiment et prix",
        "expected_topics": ["relation", "sentiment", "prix", "explication"],
        "category": "correlation",
        "difficulty": "medium",
        "ground_truth": "Explication pedagogique de la correlation avec exemples."
    },

    # ===================================================================
    # CATEGORIE 4: ANALYSE TEMPORELLE
    # ===================================================================
    {
        "question": "Comment a evolue le sentiment de Bitcoin cette semaine?",
        "expected_topics": ["evolution", "bitcoin", "semaine", "tendance"],
        "category": "temporal",
        "difficulty": "medium",
        "ground_truth": "Evolution du sentiment sur la semaine avec tendance."
    },
    {
        "question": "Le sentiment d'Ethereum s'ameliore-t-il?",
        "expected_topics": ["amelioration", "ethereum", "tendance"],
        "category": "temporal",
        "difficulty": "medium",
        "ground_truth": "Analyse de la tendance du sentiment ETH."
    },
    {
        "question": "Quel est le trend du sentiment crypto sur le dernier mois?",
        "expected_topics": ["trend", "mois", "sentiment"],
        "category": "temporal",
        "difficulty": "hard",
        "ground_truth": "Tendance mensuelle du sentiment global."
    },

    # ===================================================================
    # CATEGORIE 5: QUESTIONS DETAILLEES
    # ===================================================================
    {
        "question": "Donne-moi une analyse complete de Bitcoin",
        "expected_topics": ["bitcoin", "analyse", "complete", "sentiment", "prix"],
        "category": "detailed",
        "difficulty": "hard",
        "ground_truth": "Analyse complete: sentiment, prix, correlation, tendance."
    },
    {
        "question": "Resume la situation d'Ethereum",
        "expected_topics": ["ethereum", "resume", "situation"],
        "category": "detailed",
        "difficulty": "medium",
        "ground_truth": "Resume concis de la situation ETH."
    },
    {
        "question": "Que disent les gens sur Solana?",
        "expected_topics": ["solana", "opinions", "social"],
        "category": "detailed",
        "difficulty": "medium",
        "ground_truth": "Resume des opinions sociales sur Solana."
    },

    # ===================================================================
    # CATEGORIE 6: QUESTIONS VAGUES (Test reformulation)
    # ===================================================================
    {
        "question": "Et Solana?",
        "expected_topics": ["solana"],
        "category": "vague",
        "difficulty": "easy",
        "requires_context": True,
        "ground_truth": "La question doit etre reformulee avec le contexte precedent."
    },
    {
        "question": "Pourquoi?",
        "expected_topics": ["explication"],
        "category": "vague",
        "difficulty": "easy",
        "requires_context": True,
        "ground_truth": "La question doit etre reformulee pour demander une explication."
    },
    {
        "question": "Et les autres?",
        "expected_topics": ["autres", "cryptos"],
        "category": "vague",
        "difficulty": "easy",
        "requires_context": True,
        "ground_truth": "La question doit etre reformulee pour inclure les autres cryptos."
    },
    {
        "question": "Lequel?",
        "expected_topics": ["comparaison"],
        "category": "vague",
        "difficulty": "easy",
        "requires_context": True,
        "ground_truth": "La question doit etre reformulee pour demander une comparaison."
    },

    # ===================================================================
    # CATEGORIE 7: QUESTIONS FAQ
    # ===================================================================
    {
        "question": "Comment fonctionne le score de sentiment?",
        "expected_topics": ["score", "fonctionnement", "explication"],
        "category": "faq",
        "difficulty": "easy",
        "ground_truth": "Explication du score entre -1 et +1."
    },
    {
        "question": "Qu'est-ce que la correlation de Pearson?",
        "expected_topics": ["pearson", "correlation", "definition"],
        "category": "faq",
        "difficulty": "easy",
        "ground_truth": "Definition et explication du coefficient de Pearson."
    },
    {
        "question": "D'ou viennent les donnees?",
        "expected_topics": ["donnees", "source", "origine"],
        "category": "faq",
        "difficulty": "easy",
        "ground_truth": "Explication des sources de donnees (Twitter, Reddit)."
    },
]


# =====================================================================
# FONCTIONS UTILITAIRES
# =====================================================================

def get_test_samples(n: int = None, category: str = None, shuffle: bool = True) -> List[Dict]:
    """
    Retourne un sous-ensemble du dataset de test.

    Args:
        n: Nombre de samples (None = tous)
        category: Filtrer par categorie
        shuffle: Melanger les samples

    Returns:
        Liste de samples
    """
    samples = TEST_DATASET.copy()

    # Filtrer par categorie
    if category:
        samples = [s for s in samples if s.get("category") == category]

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


def get_categories() -> List[str]:
    """Retourne la liste des categories disponibles"""
    return list(set(s.get("category", "other") for s in TEST_DATASET))


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
        "difficulties": difficulties
    }


# =====================================================================
# QUICK EVAL SAMPLES (pour tests rapides)
# =====================================================================

QUICK_EVAL_SAMPLES = [
    {
        "question": "Quel est le sentiment actuel de Bitcoin?",
        "category": "sentiment_general",
    },
    {
        "question": "Compare le sentiment de Bitcoin et Ethereum",
        "category": "comparison",
    },
    {
        "question": "Y a-t-il une correlation entre sentiment et prix?",
        "category": "correlation",
    },
    {
        "question": "Quelle crypto a le meilleur sentiment?",
        "category": "comparison",
    },
    {
        "question": "Comment fonctionne le score de sentiment?",
        "category": "faq",
    },
]


if __name__ == "__main__":
    # Afficher les stats du dataset
    stats = get_dataset_stats()
    logger.info(f"Dataset RAGAS: {stats['total_samples']} samples")
    logger.info(f"Categories: {stats['categories']}")
    logger.info(f"Difficulties: {stats['difficulties']}")
