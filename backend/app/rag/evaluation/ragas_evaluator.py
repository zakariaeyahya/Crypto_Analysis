"""
RAGAS Evaluator pour le systeme RAG Crypto Sentiment.

Metriques evaluees:
- Faithfulness: La reponse est-elle fidele aux documents recuperes?
- Answer Relevancy: La reponse est-elle pertinente a la question?
- Context Precision: Les documents recuperes sont-ils pertinents?
- Context Recall: Tous les documents necessaires sont-ils recuperes?

Usage:
    from app.rag.evaluation import RAGASEvaluator

    evaluator = RAGASEvaluator()
    results = evaluator.evaluate_dataset(test_samples)
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.rag.logger import get_logger

logger = get_logger("ragas_evaluator")


class RAGASEvaluator:
    """
    Evaluateur RAGAS pour mesurer la qualite du systeme RAG.

    Attributes:
        llm: LLM pour l'evaluation (Groq)
        results_dir: Dossier pour sauvegarder les resultats
    """

    def __init__(self, results_dir: str = None):
        """
        Initialise l'evaluateur RAGAS.

        Args:
            results_dir: Dossier pour les resultats (defaut: backend/evaluation_results)
        """
        self.results_dir = Path(results_dir) if results_dir else self._get_default_results_dir()
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self._ragas_available = self._check_ragas_available()
        self._llm = None
        self._metrics = None

        logger.info(f"RAGASEvaluator initialise (results_dir: {self.results_dir})")

    def _get_default_results_dir(self) -> Path:
        """Retourne le dossier par defaut pour les resultats"""
        backend_dir = Path(__file__).resolve().parent.parent.parent.parent
        return backend_dir / "evaluation_results"

    def _check_ragas_available(self) -> bool:
        """Verifie si RAGAS est installe"""
        try:
            import ragas
            logger.info(f"RAGAS version: {ragas.__version__}")
            return True
        except ImportError:
            logger.warning("RAGAS non installe. Installer avec: pip install ragas")
            return False

    def _init_ragas(self):
        """Initialise RAGAS avec le LLM Groq"""
        if not self._ragas_available:
            raise ImportError("RAGAS non disponible. Installer avec: pip install ragas")

        if self._metrics is not None:
            return  # Deja initialise

        try:
            from groq import Groq
            from ragas.llms import llm_factory
            from ragas.metrics import (
                Faithfulness,
                ResponseRelevancy,
                LLMContextPrecisionWithoutReference,
                LLMContextRecall,
            )

            # Initialiser le LLM Groq pour RAGAS
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY non configure dans .env")

            client = Groq(api_key=groq_api_key)
            self._llm = llm_factory(
                model="llama-3.3-70b-versatile",
                provider="groq",
                client=client
            )

            # Initialiser les metriques
            self._metrics = {
                "faithfulness": Faithfulness(llm=self._llm),
                "answer_relevancy": ResponseRelevancy(llm=self._llm),
                "context_precision": LLMContextPrecisionWithoutReference(llm=self._llm),
            }

            logger.info("RAGAS initialise avec Groq LLM")

        except Exception as e:
            logger.error(f"Erreur initialisation RAGAS: {e}")
            raise

    def evaluate_single(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        ground_truth: str = None
    ) -> Dict[str, Any]:
        """
        Evalue une seule paire question/reponse.

        Args:
            question: Question posee
            answer: Reponse generee par le RAG
            contexts: Documents recuperes
            ground_truth: Reponse attendue (optionnel)

        Returns:
            Dict avec les scores pour chaque metrique
        """
        self._init_ragas()

        scores = {}

        try:
            # Evaluer chaque metrique
            for metric_name, metric in self._metrics.items():
                try:
                    result = asyncio.run(
                        metric.ascore(
                            user_input=question,
                            response=answer,
                            retrieved_contexts=contexts
                        )
                    )
                    scores[metric_name] = round(result.value, 3)
                except Exception as e:
                    logger.warning(f"Erreur metrique {metric_name}: {e}")
                    scores[metric_name] = None

        except Exception as e:
            logger.error(f"Erreur evaluation: {e}")
            return {"error": str(e)}

        return scores

    def evaluate_from_rag_result(self, rag_result: Dict) -> Dict[str, Any]:
        """
        Evalue a partir d'un resultat du RAG pipeline.

        Args:
            rag_result: Resultat de rag_service.process_query()

        Returns:
            Dict avec les scores
        """
        question = rag_result.get("question", "")
        answer = rag_result.get("answer", "")
        sources = rag_result.get("sources", [])

        # Extraire les textes des sources
        contexts = [s.get("text", "") for s in sources if s.get("text")]

        if not contexts:
            logger.warning("Pas de contextes dans le resultat RAG")
            return {"error": "no_contexts"}

        return self.evaluate_single(question, answer, contexts)

    def evaluate_dataset(
        self,
        samples: List[Dict],
        run_rag: bool = True,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Evalue un dataset complet.

        Args:
            samples: Liste de samples avec "question" et optionnel "ground_truth"
            run_rag: Executer le RAG pipeline (sinon utiliser les reponses existantes)
            save_results: Sauvegarder les resultats dans un fichier

        Returns:
            Dict avec resultats detailles et summary
        """
        from app.rag.rag_service import get_rag_service

        rag_service = get_rag_service() if run_rag else None

        results = []
        total_scores = {
            "faithfulness": [],
            "answer_relevancy": [],
            "context_precision": [],
        }

        logger.info(f"Evaluation de {len(samples)} samples...")

        for i, sample in enumerate(samples):
            question = sample.get("question", "")
            ground_truth = sample.get("ground_truth", sample.get("expected_answer", ""))

            logger.info(f"[{i+1}/{len(samples)}] {question[:50]}...")

            try:
                # Executer le RAG si necessaire
                if run_rag:
                    rag_result = rag_service.process_query(question)
                    answer = rag_result.get("answer", "")
                    contexts = [s.get("text", "") for s in rag_result.get("sources", [])]
                else:
                    answer = sample.get("answer", "")
                    contexts = sample.get("contexts", [])

                # Evaluer
                scores = self.evaluate_single(question, answer, contexts, ground_truth)

                # Collecter les scores
                for metric, score in scores.items():
                    if score is not None and metric in total_scores:
                        total_scores[metric].append(score)

                results.append({
                    "question": question,
                    "answer": answer[:200] + "..." if len(answer) > 200 else answer,
                    "num_contexts": len(contexts),
                    "ground_truth": ground_truth,
                    "scores": scores
                })

            except Exception as e:
                logger.error(f"Erreur sample {i+1}: {e}")
                results.append({
                    "question": question,
                    "error": str(e)
                })

        # Calculer les moyennes
        summary = {}
        for metric, values in total_scores.items():
            if values:
                summary[metric] = {
                    "mean": round(sum(values) / len(values), 3),
                    "min": round(min(values), 3),
                    "max": round(max(values), 3),
                    "count": len(values)
                }

        # Score global (moyenne des moyennes)
        means = [s["mean"] for s in summary.values() if "mean" in s]
        summary["overall"] = round(sum(means) / len(means), 3) if means else 0

        output = {
            "timestamp": datetime.now().isoformat(),
            "num_samples": len(samples),
            "num_evaluated": len([r for r in results if "scores" in r]),
            "summary": summary,
            "results": results
        }

        # Sauvegarder
        if save_results:
            self._save_results(output)

        logger.info(f"Evaluation terminee. Score global: {summary.get('overall', 'N/A')}")
        return output

    def _save_results(self, results: Dict):
        """Sauvegarde les resultats dans un fichier JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"ragas_eval_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"Resultats sauvegardes: {filename}")
        return filename

    def run_quick_eval(self, num_samples: int = 5) -> Dict[str, Any]:
        """
        Evaluation rapide avec un sous-ensemble du dataset.

        Args:
            num_samples: Nombre de samples a evaluer

        Returns:
            Resultats de l'evaluation
        """
        from .test_dataset import get_test_samples

        samples = get_test_samples(num_samples)
        return self.evaluate_dataset(samples, run_rag=True, save_results=True)

    def log_summary(self, results: Dict):
        """Affiche un resume lisible des resultats via logger"""
        summary = results.get("summary", {})

        logger.info("=" * 60)
        logger.info("              RAGAS EVALUATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Samples: {results.get('num_evaluated', 0)}/{results.get('num_samples', 0)}")
        logger.info(f"Timestamp: {results.get('timestamp', 'N/A')}")
        logger.info("-" * 60)

        for metric, stats in summary.items():
            if metric == "overall":
                continue
            if isinstance(stats, dict):
                logger.info(f"{metric:25} | Mean: {stats['mean']:.3f} | "
                            f"Min: {stats['min']:.3f} | Max: {stats['max']:.3f}")

        logger.info("-" * 60)
        overall = summary.get("overall", 0)
        status = "Excellent" if overall >= 0.8 else "Bon" if overall >= 0.6 else "A ameliorer"
        logger.info(f"{'SCORE GLOBAL':25} | {overall:.3f} ({status})")
        logger.info("=" * 60)


# =====================================================================
# EVALUATEUR SIMPLIFIE (sans RAGAS)
# =====================================================================

class SimpleEvaluator:
    """
    Evaluateur simplifie sans dependance RAGAS.
    Utilise des heuristiques pour evaluer les reponses.
    """

    def __init__(self):
        logger.info("SimpleEvaluator initialise")

    def evaluate_response(
        self,
        question: str,
        answer: str,
        contexts: List[str]
    ) -> Dict[str, float]:
        """
        Evalue une reponse avec des heuristiques simples.

        Args:
            question: Question posee
            answer: Reponse generee
            contexts: Contextes recuperes

        Returns:
            Scores heuristiques
        """
        scores = {}

        # 1. Longueur de reponse (reponse substantielle?)
        answer_len = len(answer.split())
        scores["response_length"] = min(1.0, answer_len / 100)

        # 2. Couverture du contexte (mots du contexte dans la reponse)
        context_words = set()
        for ctx in contexts:
            context_words.update(ctx.lower().split())

        answer_words = set(answer.lower().split())
        if context_words:
            coverage = len(answer_words & context_words) / len(context_words)
            scores["context_coverage"] = min(1.0, coverage * 2)
        else:
            scores["context_coverage"] = 0.0

        # 3. Pertinence question (mots de la question dans la reponse)
        question_words = set(question.lower().split())
        question_coverage = len(answer_words & question_words) / max(len(question_words), 1)
        scores["question_relevance"] = min(1.0, question_coverage * 3)

        # 4. Presence de crypto mentionnees
        crypto_keywords = ["bitcoin", "btc", "ethereum", "eth", "solana", "sol"]
        has_crypto = any(kw in answer.lower() for kw in crypto_keywords)
        scores["crypto_mention"] = 1.0 if has_crypto else 0.5

        # Score global
        scores["overall"] = round(sum(scores.values()) / len(scores), 3)

        return scores

    def evaluate_dataset(
        self,
        samples: List[Dict],
        run_rag: bool = True
    ) -> Dict[str, Any]:
        """
        Evalue un dataset avec les heuristiques simples.
        """
        from app.rag.rag_service import get_rag_service

        rag_service = get_rag_service() if run_rag else None

        results = []
        all_scores = []

        for sample in samples:
            question = sample.get("question", "")

            if run_rag:
                rag_result = rag_service.process_query(question)
                answer = rag_result.get("answer", "")
                contexts = [s.get("text", "") for s in rag_result.get("sources", [])]
            else:
                answer = sample.get("answer", "")
                contexts = sample.get("contexts", [])

            scores = self.evaluate_response(question, answer, contexts)
            all_scores.append(scores["overall"])

            results.append({
                "question": question,
                "scores": scores
            })

        return {
            "num_samples": len(samples),
            "average_score": round(sum(all_scores) / len(all_scores), 3) if all_scores else 0,
            "results": results
        }
