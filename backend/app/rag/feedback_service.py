"""
Service de gestion des feedbacks utilisateur pour le chatbot RAG.
Stocke les feedbacks dans un fichier JSON pour analyse ulterieure.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from app.rag.logger import get_logger

logger = get_logger("feedback_service")

# Chemin du fichier de stockage des feedbacks
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
FEEDBACK_DIR = BACKEND_DIR / "feedback_data"
FEEDBACK_FILE = FEEDBACK_DIR / "feedbacks.json"


class FeedbackService:
    """Service pour collecter et analyser les feedbacks utilisateur"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Creer le dossier si necessaire
        try:
            FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create feedback directory: {e}")

        self._initialized = True
        logger.info(f"FeedbackService initialized. Storage: {FEEDBACK_FILE}")

    def _load_feedbacks(self) -> List[Dict]:
        """Charge les feedbacks existants depuis le fichier JSON"""
        if not FEEDBACK_FILE.exists():
            return []

        try:
            with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading feedbacks: {e}")
            return []

    def _save_feedbacks(self, feedbacks: List[Dict]) -> bool:
        """Sauvegarde les feedbacks dans le fichier JSON"""
        try:
            with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
                json.dump(feedbacks, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving feedbacks: {e}")
            return False

    def add_feedback(
        self,
        message_id: str,
        question: str,
        answer: str,
        feedback_type: str,  # "positive" ou "negative"
        session_id: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Dict:
        """
        Ajoute un nouveau feedback.

        Args:
            message_id: ID unique du message
            question: Question posee par l'utilisateur
            answer: Reponse du chatbot
            feedback_type: "positive" (thumbs up) ou "negative" (thumbs down)
            session_id: ID de session optionnel
            comment: Commentaire optionnel de l'utilisateur

        Returns:
            Dict avec le feedback cree et son ID
        """
        feedbacks = self._load_feedbacks()

        feedback = {
            "id": f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(feedbacks)}",
            "message_id": message_id,
            "question": question,
            "answer": answer,
            "feedback_type": feedback_type,
            "session_id": session_id,
            "comment": comment,
            "timestamp": datetime.now().isoformat(),
        }

        feedbacks.append(feedback)

        if self._save_feedbacks(feedbacks):
            logger.info(f"Feedback saved: {feedback['id']} ({feedback_type})")
            return {"status": "success", "feedback_id": feedback["id"]}
        else:
            logger.error("Failed to save feedback")
            return {"status": "error", "message": "Failed to save feedback"}

    def get_feedbacks(
        self,
        feedback_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Recupere les feedbacks avec filtres optionnels.

        Args:
            feedback_type: Filtrer par type ("positive" ou "negative")
            limit: Nombre max de feedbacks a retourner

        Returns:
            Liste des feedbacks
        """
        feedbacks = self._load_feedbacks()

        # Filtrer par type si specifie
        if feedback_type:
            feedbacks = [f for f in feedbacks if f.get("feedback_type") == feedback_type]

        # Trier par date (plus recent en premier)
        feedbacks.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return feedbacks[:limit]

    def get_stats(self) -> Dict:
        """
        Retourne les statistiques des feedbacks.

        Returns:
            Dict avec total, positifs, negatifs, et ratio
        """
        feedbacks = self._load_feedbacks()

        total = len(feedbacks)
        positive = sum(1 for f in feedbacks if f.get("feedback_type") == "positive")
        negative = sum(1 for f in feedbacks if f.get("feedback_type") == "negative")

        ratio = positive / total if total > 0 else 0

        stats = {
            "total": total,
            "positive": positive,
            "negative": negative,
            "positive_ratio": round(ratio, 3),
            "negative_ratio": round(1 - ratio, 3) if total > 0 else 0
        }

        logger.info(f"Feedback stats: {stats}")
        return stats


# Singleton instance
_feedback_service = None

def get_feedback_service() -> FeedbackService:
    """Retourne l'instance singleton du FeedbackService"""
    global _feedback_service
    if _feedback_service is None:
        _feedback_service = FeedbackService()
    return _feedback_service
