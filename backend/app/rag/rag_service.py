"""
Orchestration du pipeline RAG complet: Retrieval → Generation.
Avec support de la memoire conversationnelle et reformulation de requetes.
"""

import re
import time
from app.rag.llm_service import get_llm_service
from app.rag.config import RAG_TOP_K
from app.rag.logger import get_logger
from app.rag.memory_service import get_memory_service
from .retriever_service import get_retriever_service


logger = get_logger("rag_service")

# Mots-cles vagues qui necessitent reformulation
VAGUE_PATTERNS = [
    r"^pourquoi\??$",
    r"^comment\??$",
    r"^et\s+\w+\??$",  # "et solana?", "et lui?"
    r"^quoi\??$",
    r"^lequel\??$",
    r"^laquelle\??$",
    r"^c'est quoi\??$",
    r"^explique\??$",
    r"^details?\??$",
    r"^plus\??$",
]


class RAGService:
    """Service d'orchestration du pipeline RAG complet"""

    def __init__(self):
        """Initialise le service RAG"""
        self.retriever = None  # Lazy loading
        self.llm = None  # Lazy loading
        self.memory = None  # Lazy loading
        self.top_k = RAG_TOP_K
        self.include_sources = True
        logger.info(f"RAGService initialise: top_k={RAG_TOP_K}")

    def _init_services(self):
        """Initialise les services (lazy loading)"""
        if self.retriever is None:
            self.retriever = get_retriever_service()
        if self.llm is None:
            self.llm = get_llm_service()
        if self.memory is None:
            self.memory = get_memory_service()

    def _is_vague_query(self, query: str) -> bool:
        """Detecte si une requete est trop vague pour la recherche"""
        query_lower = query.lower().strip()

        # Moins de 3 mots = probablement vague
        if len(query_lower.split()) < 3:
            return True

        # Verifier les patterns vagues
        for pattern in VAGUE_PATTERNS:
            if re.match(pattern, query_lower, re.IGNORECASE):
                return True

        return False

    def _reformulate_query(self, query: str, history: list) -> str:
        """
        Reformule une requete vague en utilisant l'historique

        Args:
            query: Requete originale (ex: "Pourquoi?")
            history: Liste des messages precedents

        Returns:
            Requete enrichie (ex: "Pourquoi Bitcoin a le meilleur sentiment?")
        """
        if not history:
            return query

        # Extraire le contexte des derniers messages
        context_parts = []

        # Chercher les cryptos mentionnees
        cryptos_mentioned = set()
        topics = []

        for msg in history[-4:]:  # Derniers 4 messages
            content = msg.get("content", "")

            # Detecter les cryptos
            if "bitcoin" in content.lower() or "btc" in content.lower():
                cryptos_mentioned.add("Bitcoin")
            if "ethereum" in content.lower() or "eth" in content.lower():
                cryptos_mentioned.add("Ethereum")
            if "solana" in content.lower() or "sol" in content.lower():
                cryptos_mentioned.add("Solana")

            # Detecter les sujets
            if "sentiment" in content.lower():
                topics.append("sentiment")
            if "prix" in content.lower() or "price" in content.lower():
                topics.append("prix")
            if "correlation" in content.lower():
                topics.append("correlation")

        # Construire la requete enrichie
        query_lower = query.lower().strip()

        if query_lower in ["pourquoi?", "pourquoi"]:
            # "Pourquoi?" -> "Pourquoi [crypto] a [topic]?"
            if cryptos_mentioned and topics:
                crypto = list(cryptos_mentioned)[-1]
                topic = topics[-1]
                return f"Pourquoi {crypto} a ce {topic}? Explique les raisons."
            elif cryptos_mentioned:
                crypto = list(cryptos_mentioned)[-1]
                return f"Pourquoi {crypto}? Donne plus de details sur cette crypto."

        elif query_lower.startswith("et "):
            # "Et Solana?" -> "Quel est le sentiment de Solana?"
            match = re.match(r"et\s+(\w+)\??", query_lower)
            if match:
                crypto = match.group(1).capitalize()
                if topics:
                    topic = topics[-1]
                    return f"Quel est le {topic} de {crypto}?"
                return f"Parle-moi de {crypto}. Quel est son sentiment?"

        elif query_lower in ["comment?", "comment"]:
            if cryptos_mentioned:
                crypto = list(cryptos_mentioned)[-1]
                return f"Comment evolue {crypto}? Explique la tendance."

        elif query_lower in ["lequel?", "laquelle?", "lequel", "laquelle"]:
            if topics:
                return f"Quelle crypto a le meilleur {topics[-1]}? Compare les."
            return "Quelle crypto est la meilleure? Compare Bitcoin, Ethereum et Solana."

        # Si pas de reformulation specifique, enrichir avec le contexte
        if cryptos_mentioned:
            cryptos_str = ", ".join(cryptos_mentioned)
            return f"{query} (contexte: {cryptos_str})"

        return query

    def process_query(self, question, crypto=None, top_k=None, session_id=None):
        """
        Execute le pipeline RAG complet: Retrieval + Generation

        Args:
            question (str): Question de l'utilisateur
            crypto (str): Crypto specifique (optionnel)
            top_k (int): Nombre de documents a recuperer
            session_id (str): ID de session pour la memoire conversationnelle

        Returns:
            dict: Reponse avec sources et metadonnees
        """
        self._init_services()

        start_time = time.time()
        top_k = top_k or self.top_k

        logger.info(f"Traitement RAG: '{question[:80]}...' (session: {session_id})")

        # =====================================================================
        # ETAPE 0: Gerer la memoire conversationnelle
        # =====================================================================
        history_text = ""
        history_messages = []
        if session_id:
            # Ajouter la question actuelle a l'historique
            self.memory.add_message(session_id, "user", question)
            # Recuperer l'historique formate (sans la question actuelle)
            history_text = self.memory.get_history_as_text(session_id)
            history_messages = self.memory.get_history(session_id)
            if history_text:
                logger.info(f"Historique recupere: {len(history_text)} chars")

        # =====================================================================
        # ETAPE 0.5: Reformuler les requetes vagues
        # =====================================================================
        search_query = question
        if self._is_vague_query(question) and history_messages:
            search_query = self._reformulate_query(question, history_messages)
            if search_query != question:
                logger.info(f"Requete reformulee: '{question}' -> '{search_query}'")

        # =====================================================================
        # ETAPE 1: RETRIEVAL - Recuperer les documents pertinents
        # =====================================================================
        try:
            retrieval_result = self.retriever.retrieve_with_context(
                query=search_query,  # Utiliser la requete reformulee
                top_k=top_k
            )
        except Exception as e:
            logger.error(f"❌ Erreur retrieval: {e}")
            return {
                "question": question,
                "answer": "Erreur lors de la recherche de documents.",
                "sources": [],
                "metadata": {
                    "num_sources": 0,
                    "processing_time": time.time() - start_time,
                    "model_used": "none",
                    "error": str(e),
                }
            }

        # =====================================================================
        # ÉTAPE 2: Vérifier si documents trouvés
        # =====================================================================
        if retrieval_result["num_results"] == 0:
            logger.warning("⚠️ Aucun document pertinent trouvé")
            return {
                "question": question,
                "answer": "Je n'ai pas trouvé d'informations pertinentes pour répondre à cette question.",
                "sources": [],
                "metadata": {
                    "num_sources": 0,
                    "processing_time": round(time.time() - start_time, 2),
                    "model_used": "none",
                    "query_type": retrieval_result.get("query_type", "unknown"),
                }
            }

        # =====================================================================
        # ETAPE 3: GENERATION - Generer la reponse avec LLM + historique
        # =====================================================================
        answer = None
        try:
            context = retrieval_result["context"]
            query_type = retrieval_result.get("query_type", "general")  # ✅ Récupérer le type
            
            # ✅ Transmettre le type au LLM
            answer = self.llm.generate_with_context(
                question=question,
                context=context,
                history=history_text  # Passer l'historique au LLM
            )
            logger.info(f"Reponse generee ({len(answer)} caracteres)")

        except Exception as e:
            logger.warning(f"LLM error: {e}, utilisation du fallback")
            answer = self._generate_fallback_answer(retrieval_result["documents"])

        # =====================================================================
        # ETAPE 3.5: Sauvegarder la reponse dans la memoire
        # =====================================================================
        if session_id and answer:
            self.memory.add_message(session_id, "assistant", answer)

        # =====================================================================
        # ETAPE 4: Construire la réponse finale
        # =====================================================================
        sources = []
        if self.include_sources:
            for i, doc in enumerate(retrieval_result["documents"], 1):
                source = {
                    "id": doc["id"],
                    "rank": i,
                    "type": doc["metadata"].get("type", "unknown"),
                    "crypto": doc["metadata"].get("crypto", "UNKNOWN"),
                    "date": doc["metadata"].get("date", "N/A"),
                    "source": doc["metadata"].get("source", "system"),
                    "text": doc["text"][:200] + "...",
                    "score": round(doc["score"], 3),
                }
                sources.append(source)

        processing_time = round(time.time() - start_time, 2)

        result = {
            "question": question,
            "answer": answer,
            "sources": sources,
            "metadata": {
                "num_sources": len(sources),
                "processing_time": processing_time,
                "model_used": self.llm.provider,
                "top_k": top_k,
                "session_id": session_id,
                "has_history": bool(history_text),
                "query_reformulated": search_query != question,
                "search_query": search_query if search_query != question else None,
            }
        }

        logger.info(f"Pipeline RAG complete ({processing_time}s, {len(sources)} sources)")
        return result

    def _generate_fallback_answer(self, documents, query_type="general"):
        """
        ✅ AMÉLIORÉ: Génère une réponse intelligente sans LLM
        
        S'adapte au type de question
        """
        if not documents:
            return "Aucune information trouvée."

        # ✅ NOUVEAU: Adapter le fallback selon le type
        if query_type == "price" and documents:
            # Pour les prix, chercher spécifiquement les documents de prix
            price_docs = [d for d in documents if d["metadata"].get("type") == "price"]
            if price_docs:
                doc = price_docs[0]
                return (
                    f"💰 PRIX:\n"
                    f"{doc['text']}\n\n"
                    f"(Réponse en mode fallback)"
                )

        elif query_type == "sentiment" and documents:
            # Pour le sentiment, utiliser les posts
            sentiment_docs = [d for d in documents if d["metadata"].get("type") in ["post", "daily_summary"]]
            if sentiment_docs:
                doc = sentiment_docs[0]
                return (
                    f"📊 SENTIMENT:\n"
                    f"{doc['text']}\n\n"
                    f"(Réponse en mode fallback)"
                )

        # Fallback générique pour les autres types
        top_doc = documents[0]
        doc_type = top_doc["metadata"].get("type", "document")
        crypto = top_doc["metadata"].get("crypto", "UNKNOWN")
        text = top_doc["text"][:300]

        answer = (
            f"Voici ce que j'ai trouvé ({doc_type} - {crypto}):\n\n"
            f"{text}...\n\n"
            f"(Mode fallback - LLM non disponible)"
        )

        logger.debug("Fallback answer généré")
        return answer

    def get_quick_answer(self, question):
        """
        Retourne une réponse rapide (sans métadonnées détaillées)
        """
        result = self.process_query(question)
        return result["answer"]

    def get_crypto_summary(self, crypto):
        """
        Retourne un résumé complet d'une crypto
        """
        question = (
            f"Donne-moi un résumé complet de {crypto}: "
            f"sentiment actuel, tendance récente, prix historique, et analyse de corrélation "
            f"avec le prix."
        )

        result = self.process_query(question, crypto=crypto, top_k=7)
        logger.info(f"Résumé crypto généré: {crypto}")
        return result

    def compare_cryptos(self, cryptos):
        """
        Compare le sentiment et prix de plusieurs cryptos
        """
        crypto_names = ", ".join(cryptos)
        question = (
            f"Compare le sentiment et les prix de {crypto_names}. "
            f"Lequel a le meilleur sentiment actuellement? "
            f"Lequel a augmenté le plus en pourcentage? "
            f"Explique les différences."
        )

        result = self.process_query(question, top_k=10)
        logger.info(f"Comparaison générée: {crypto_names}")
        return result

    def get_trending_topics(self, top_k=5):
        """
        Retourne les sujets tendance du moment
        """
        question = "Quels sont les sujets les plus discutés actuellement dans la communauté crypto?"

        result = self.process_query(question, top_k=top_k)
        logger.info(f"Sujets tendance récupérés (top {top_k})")
        return result

    def get_sentiment_analysis(self, crypto, days=7):
        """
        Analyse le sentiment pour une crypto sur une période
        """
        question = (
            f"Analyse le sentiment pour {crypto} sur les {days} derniers jours. "
            f"Le sentiment est-il positif, négatif ou neutre? Pourquoi?"
        )

        result = self.process_query(question, crypto=crypto, top_k=8)
        logger.info(f"Analyse sentiment générée: {crypto}")
        return result

    def health_check(self):
        """
        Vérifie l'état de tous les composants du système
        """
        logger.info("🥇 Health check en cours...")

        self._init_services()

        status = {
            "rag_service": "ok",
            "retriever": "unknown",
            "llm": "unknown",
            "pinecone": "unknown",
        }

        # =====================================================================
        # Vérifier Retriever
        # =====================================================================
        try:
            self.retriever._init_services()
            status["retriever"] = "ok"
        except Exception as e:
            logger.error(f"❌ Retriever error: {e}")
            status["retriever"] = "error"

        # =====================================================================
        # Vérifier LLM
        # =====================================================================
        try:
            if self.llm.is_available():
                info = self.llm.get_provider_info()
                status["llm"] = f"ok ({info['provider']})"
            else:
                status["llm"] = "unavailable"
        except Exception as e:
            logger.error(f"❌ LLM error: {e}")
            status["llm"] = "error"

        # =====================================================================
        # Vérifier Pinecone
        # =====================================================================
        try:
            stats = self.retriever.pinecone_service.get_stats()
            total_vectors = stats.get("total_vectors", 0)
            status["pinecone"] = f"ok ({total_vectors} vectors)"
        except Exception as e:
            logger.error(f"❌ Pinecone error: {e}")
            status["pinecone"] = "error"

        # =====================================================================
        # Déterminer le statut global
        # =====================================================================
        errors = [v for v in status.values() if v == "error"]
        unavailable = [v for v in status.values() if v == "unavailable"]

        if not errors:
            status["overall"] = "ok"
        elif len(errors) >= 2:
            status["overall"] = "error"
        else:
            status["overall"] = "degraded"

        logger.info(f"Health check: {status['overall']}")
        return status

    def set_include_sources(self, include_sources):
        """
        Configure l'inclusion des sources dans les réponses
        """
        self.include_sources = include_sources
        logger.info(f"Include sources: {include_sources}")

    def get_config(self):
        """
        Retourne la configuration courante du service

        Returns:
            dict: Configuration
        """
        return {
            "top_k": self.top_k,
            "include_sources": self.include_sources,
            "retriever_initialized": self.retriever is not None,
            "llm_initialized": self.llm is not None,
        }

    def clear_session(self, session_id: str):
        """
        Efface l'historique d'une session

        Args:
            session_id: ID de la session a effacer
        """
        self._init_services()
        self.memory.clear_session(session_id)
        logger.info(f"Session {session_id} effacee")

    def get_session_info(self, session_id: str):
        """
        Retourne les infos d'une session

        Args:
            session_id: ID de la session

        Returns:
            dict: Informations de la session
        """
        self._init_services()
        return self.memory.get_session_info(session_id)


# =====================================================================
# SINGLETON GLOBAL
# =====================================================================
_rag_service = None


def get_rag_service():
    """
    Retourne une instance unique du service RAG (singleton)
    """
    global _rag_service

    if _rag_service is None:
        _rag_service = RAGService()
        logger.info("✓ Singleton RAGService créé")

    return _rag_service