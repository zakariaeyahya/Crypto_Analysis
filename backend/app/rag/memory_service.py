"""
Service de memoire conversationnelle pour le chatbot RAG
Garde l'historique des conversations par session
"""

from typing import List, Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta
from app.rag.logger import get_logger

logger = get_logger("memory_service")

# Configuration
MAX_HISTORY_LENGTH = 10  # Nombre max de messages a garder par session
SESSION_TIMEOUT_MINUTES = 30  # Expire apres 30 min d'inactivite


class ConversationMemory:
    """Gere l'historique des conversations par session"""

    def __init__(self, max_history: int = MAX_HISTORY_LENGTH):
        self.max_history = max_history
        # Structure: {session_id: {"messages": [...], "last_activity": datetime}}
        self.sessions: Dict[str, Dict] = defaultdict(lambda: {
            "messages": [],
            "last_activity": datetime.now()
        })

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Ajoute un message a l'historique de la session

        Args:
            session_id: Identifiant de session
            role: 'user' ou 'assistant'
            content: Contenu du message
        """
        session = self.sessions[session_id]
        session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        session["last_activity"] = datetime.now()

        # Garder seulement les N derniers messages
        if len(session["messages"]) > self.max_history:
            session["messages"] = session["messages"][-self.max_history:]

        logger.info(f"Session {session_id}: {len(session['messages'])} messages")

    def get_history(self, session_id: str) -> List[Dict]:
        """Retourne l'historique de la session"""
        self._cleanup_expired_sessions()
        return self.sessions[session_id]["messages"]

    def get_history_as_text(self, session_id: str) -> str:
        """
        Retourne l'historique formate comme texte pour le prompt

        Returns:
            String formate: "User: ... \nAssistant: ..."
        """
        messages = self.get_history(session_id)
        if not messages:
            return ""

        lines = []
        for msg in messages[:-1]:  # Exclure le dernier message (question actuelle)
            role = "Utilisateur" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")

        return "\n".join(lines)

    def clear_session(self, session_id: str) -> None:
        """Efface l'historique d'une session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session {session_id} cleared")

    def _cleanup_expired_sessions(self) -> None:
        """Supprime les sessions expirees"""
        now = datetime.now()
        expired = []

        for session_id, data in self.sessions.items():
            if now - data["last_activity"] > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                expired.append(session_id)

        for session_id in expired:
            del self.sessions[session_id]
            logger.info(f"Session {session_id} expired and removed")

    def get_session_info(self, session_id: str) -> Dict:
        """Retourne les infos de la session"""
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "message_count": len(session["messages"]),
            "last_activity": session["last_activity"].isoformat()
        }


# Singleton global
_memory_service: Optional[ConversationMemory] = None


def get_memory_service() -> ConversationMemory:
    """Retourne l'instance singleton du service de memoire"""
    global _memory_service
    if _memory_service is None:
        _memory_service = ConversationMemory()
        logger.info("ConversationMemory service initialized")
    return _memory_service
