#!/usr/bin/env python3
"""
Script d'evaluation RAGAS pour le systeme RAG Crypto Sentiment.

Usage:
    # Evaluation rapide (5 samples, heuristiques)
    python scripts/evaluate_rag.py --quick

    # Evaluation complete avec RAGAS
    python scripts/evaluate_rag.py --full

    # Evaluation avec nombre de samples specifique
    python scripts/evaluate_rag.py --samples 10

    # Evaluation par categorie
    python scripts/evaluate_rag.py --category comparison

    # Mode simple (sans RAGAS, heuristiques seulement)
    python scripts/evaluate_rag.py --simple

Resultats sauvegardes dans: backend/evaluation_results/
"""

import argparse
import sys
import os
from pathlib import Path

# Ajouter le chemin du backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

# Logger
from app.rag.logger import get_logger
logger = get_logger("evaluate_rag")


def run_simple_evaluation(samples: list):
    """Execute l'evaluation simple (heuristiques)"""
    from app.rag.evaluation.ragas_evaluator import SimpleEvaluator

    logger.info("=" * 60)
    logger.info("        EVALUATION SIMPLE (Heuristiques)")
    logger.info("=" * 60)

    evaluator = SimpleEvaluator()
    results = evaluator.evaluate_dataset(samples, run_rag=True)

    logger.info(f"Samples evalues: {results['num_samples']}")
    logger.info(f"Score moyen: {results['average_score']:.3f}")

    logger.info("Details par question:")
    logger.info("-" * 60)

    for r in results["results"]:
        q = r["question"][:40] + "..." if len(r["question"]) > 40 else r["question"]
        score = r["scores"]["overall"]
        logger.info(f"  {q:45} | {score:.3f}")

    return results


def run_ragas_evaluation(samples: list, save: bool = True):
    """Execute l'evaluation RAGAS complete"""
    from app.rag.evaluation.ragas_evaluator import RAGASEvaluator

    logger.info("=" * 60)
    logger.info("        EVALUATION RAGAS")
    logger.info("=" * 60)

    try:
        evaluator = RAGASEvaluator()
        results = evaluator.evaluate_dataset(
            samples,
            run_rag=True,
            save_results=save
        )

        evaluator.log_summary(results)
        return results

    except ImportError as e:
        logger.warning(f"RAGAS non disponible: {e}")
        logger.info("Installation: pip install ragas")
        logger.info("Utilisation du mode simple (heuristiques)...")
        return run_simple_evaluation(samples)


def test_single_query(question: str):
    """Teste une seule question"""
    from app.rag.rag_service import get_rag_service
    from app.rag.evaluation.ragas_evaluator import SimpleEvaluator

    logger.info(f"Question: {question}")
    logger.info("-" * 60)

    rag = get_rag_service()
    result = rag.process_query(question)

    logger.info(f"Reponse: {result['answer'][:300]}...")
    logger.info(f"Sources: {result['metadata']['num_sources']}")
    logger.info(f"Temps: {result['metadata']['processing_time']}s")

    # Evaluation simple
    evaluator = SimpleEvaluator()
    contexts = [s.get("text", "") for s in result.get("sources", [])]
    scores = evaluator.evaluate_response(question, result["answer"], contexts)

    logger.info("Scores heuristiques:")
    for metric, score in scores.items():
        logger.info(f"   {metric}: {score:.3f}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluation RAGAS du systeme RAG Crypto Sentiment"
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Evaluation rapide (5 samples, heuristiques)"
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Evaluation complete avec RAGAS"
    )

    parser.add_argument(
        "--simple",
        action="store_true",
        help="Mode simple (heuristiques seulement, pas de RAGAS)"
    )

    parser.add_argument(
        "--samples",
        type=int,
        default=5,
        help="Nombre de samples a evaluer (defaut: 5)"
    )

    parser.add_argument(
        "--category",
        type=str,
        choices=["sentiment_general", "comparison", "correlation", "temporal", "detailed", "vague", "faq"],
        help="Filtrer par categorie"
    )

    parser.add_argument(
        "--query",
        type=str,
        help="Tester une seule question"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Afficher les statistiques du dataset"
    )

    args = parser.parse_args()

    # Afficher les stats
    if args.stats:
        from app.rag.evaluation.test_dataset import get_dataset_stats, get_categories

        stats = get_dataset_stats()
        logger.info("Dataset RAGAS Statistics")
        logger.info("=" * 40)
        logger.info(f"Total samples: {stats['total_samples']}")
        logger.info("Categories:")
        for cat, count in stats["categories"].items():
            logger.info(f"  - {cat}: {count}")
        logger.info("Difficultes:")
        for diff, count in stats["difficulties"].items():
            logger.info(f"  - {diff}: {count}")
        return

    # Tester une seule question
    if args.query:
        test_single_query(args.query)
        return

    # Charger les samples
    from app.rag.evaluation.test_dataset import get_test_samples, QUICK_EVAL_SAMPLES

    if args.quick:
        samples = QUICK_EVAL_SAMPLES
        logger.info(f"Mode rapide: {len(samples)} samples")
        run_simple_evaluation(samples)
        return

    if args.category:
        samples = get_test_samples(n=args.samples, category=args.category)
        logger.info(f"Categorie '{args.category}': {len(samples)} samples")
    else:
        samples = get_test_samples(n=args.samples)
        logger.info(f"{len(samples)} samples selectionnes")

    # Executer l'evaluation
    if args.simple:
        run_simple_evaluation(samples)
    elif args.full:
        run_ragas_evaluation(samples)
    else:
        # Par defaut: simple
        run_simple_evaluation(samples)


if __name__ == "__main__":
    main()
