"""
Orchestration du pipeline RAG complet: Retrieval → Generation.

CORRECTIONS APPLIQUÉES:
✅ Transmettre query_type au LLM
✅ Améliorer le fallback selon le type
✅ Ajouter query_type aux métadonnées
"""

import time
from app.rag.llm_service import get_llm_service
from app.rag.config import RAG_TOP_K
from app.rag.logger import get_logger
from .retriever_service import get_retriever_service


logger = get_logger("rag_service")


class RAGService:
    """Service d'orchestration du pipeline RAG complet"""

    def __init__(self):
        """Initialise le service RAG"""
        self.retriever = None  # Lazy loading
        self.llm = None  # Lazy loading
        self.top_k = RAG_TOP_K
        self.include_sources = True
        logger.info(f"RAGService initialisé: top_k={RAG_TOP_K}")

    def _init_services(self):
        """Initialise les services (lazy loading)"""
        if self.retriever is None:
            self.retriever = get_retriever_service()
        if self.llm is None:
            self.llm = get_llm_service()

    def process_query(self, question, crypto=None, top_k=None):
        """
        ✅ AMÉLIORÉ: Exécute le pipeline RAG avec gestion par type
        
        Retourne:
            {
                "question": str,
                "answer": str,
                "sources": list,
                "metadata": {
                    "query_type": "price" | "sentiment" | "analysis" | "general",
                    "num_sources": int,
                    "processing_time": float,
                    ...
                }
            }
        """
        self._init_services()

        start_time = time.time()
        top_k = top_k or self.top_k

        logger.info(f"🔄 Traitement RAG: '{question[:80]}...'")

        # =====================================================================
        # ÉTAPE 1: RETRIEVAL - Récupérer les documents pertinents
        # =====================================================================
        try:
            retrieval_result = self.retriever.retrieve_with_context(
                query=question,
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
        # ÉTAPE 3: GENERATION - Générer la réponse avec LLM
        # =====================================================================
        answer = None
        try:
            context = retrieval_result["context"]
            query_type = retrieval_result.get("query_type", "general")  # ✅ Récupérer le type
            
            # ✅ Transmettre le type au LLM
            answer = self.llm.generate_with_context(
                question=question,
                context=context,
                query_type=query_type  # ✅ NOUVEAU
            )
            logger.info(f"✓ Réponse générée ({len(answer)} caractères)")

        except Exception as e:
            logger.warning(f"⚠️ LLM error: {e}, utilisation du fallback")
            answer = self._generate_fallback_answer(
                retrieval_result["documents"],
                retrieval_result.get("query_type", "general")
            )

        # =====================================================================
        # ÉTAPE 4: Construire la réponse finale
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
                "query_type": retrieval_result.get("query_type", "general"),  # ✅ NOUVEAU
            }
        }

        logger.info(f"✓ Pipeline RAG complété ({processing_time}s)")
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
        """
        return {
            "top_k": self.top_k,
            "include_sources": self.include_sources,
            "retriever_initialized": self.retriever is not None,
            "llm_initialized": self.llm is not None,
        }


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