"""
Recherche les documents pertinents pour une question utilisateur.

CORRECTIONS APPLIQUÉES:
✅ Ajouter detect_query_type() - Détecte prix/sentiment/analyse
✅ Adapter retrieve() par type de document
✅ Améliorer retrieve_with_context()
"""

from app.rag.config import RAG_TOP_K, RAG_MIN_SCORE
from app.rag.embedding_service import get_embedding_service
from app.rag.pinecone_service import get_pinecone_service
from app.rag.logger import get_logger

logger = get_logger("retriever_service")


class RetrieverService:
    """Service pour récupérer les documents pertinents"""

    def __init__(self):
        """Initialise le service de retrieval"""
        self.embedding_service = None  # Lazy loading
        self.pinecone_service = None  # Lazy loading
        self.default_top_k = RAG_TOP_K
        self.min_score = RAG_MIN_SCORE
        logger.info(f"RetrieverService initialisé: top_k={RAG_TOP_K}, min_score={RAG_MIN_SCORE}")

    def _init_services(self):
        """Initialise les services (lazy loading)"""
        if self.embedding_service is None:
            self.embedding_service = get_embedding_service()
        if self.pinecone_service is None:
            self.pinecone_service = get_pinecone_service()

    # =====================================================================
    # ✅ NOUVEAU: Détection du type de question
    # =====================================================================
    
    def detect_query_type(self, query):
        """
        ✅ NOUVEAU: Détecte le type de question
        
        Retourne: "price", "sentiment", "analysis", ou "general"
        """
        query_lower = query.lower()
        
        # Mots-clés pour les questions de prix
        price_keywords = [
            "prix", "price", "coût", "combien", "how much", 
            "$", "dollar", "euros", "€", "valeur", "value",
            "trading", "échange", "exchange", "marché", "market"
        ]
        
        # Mots-clés pour les questions de sentiment
        sentiment_keywords = [
            "sentiment", "opinion", "avis", "bullish", "bearish",
            "haussier", "baissier", "ressenti", "mood", "feeling",
            "optimisme", "pessimisme", "confiance", "peur", "fear"
        ]
        
        # Mots-clés pour les questions d'analyse
        analysis_keywords = [
            "corrélation", "correlation", "lag", "délai",
            "tendance", "trend", "pattern", "analyse", "analysis",
            "historique", "historical", "comparaison", "compare"
        ]
        
        # Compter les correspondances
        price_score = sum(1 for kw in price_keywords if kw in query_lower)
        sentiment_score = sum(1 for kw in sentiment_keywords if kw in query_lower)
        analysis_score = sum(1 for kw in analysis_keywords if kw in query_lower)
        
        # Retourner le type avec le meilleur score
        scores = {
            "price": price_score,
            "sentiment": sentiment_score,
            "analysis": analysis_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return "general"
        
        query_type = max(scores, key=scores.get)
        logger.debug(f"Type détecté: {query_type}")
        return query_type

    def extract_crypto_from_query(self, query):
        """
        Détecte la crypto mentionnée dans la question
        
        Retourne: "BTC", "ETH", "SOL", ou None
        """
        query_lower = query.lower()

        # Mapping des cryptos avec leurs keywords
        crypto_mapping = {
            "BTC": ["btc", "bitcoin", "satoshi"],
            "ETH": ["eth", "ethereum", "ether"],
            "SOL": ["sol", "solana"],
        }

        # Chercher la première crypto mentionnée
        for crypto, keywords in crypto_mapping.items():
            for keyword in keywords:
                if keyword in query_lower:
                    logger.debug(f"Crypto détectée: {crypto}")
                    return crypto

        logger.debug("Pas de crypto détectée dans la requête")
        return None

    def build_filter(self, crypto=None, doc_type=None, source=None):
        """
        Construit le filtre Pinecone pour les recherches
        """
        conditions = {}

        if crypto:
            conditions["crypto"] = {"$eq": crypto}

        if doc_type:
            conditions["type"] = {"$eq": doc_type}

        if source:
            conditions["source"] = {"$eq": source}

        if not conditions:
            return None

        # Si plusieurs conditions, utiliser $and
        if len(conditions) > 1:
            return {
                "$and": [
                    {k: v} for k, v in conditions.items()
                ]
            }

        return conditions

    def retrieve(self, query, top_k=None, crypto=None, doc_type=None, auto_detect_crypto=True):
        """
        Recherche les documents pertinents
        
        ✅ AMÉLIORÉ: Ajoute support pour doc_type
        """
        self._init_services()
        
        top_k = top_k or self.default_top_k

        # Auto-détecter la crypto si non spécifiée
        if crypto is None and auto_detect_crypto:
            crypto = self.extract_crypto_from_query(query)

        logger.info(f"🔍 Recherche: '{query[:100]}...' (top_k={top_k}, crypto={crypto}, type={doc_type})")

        # Générer l'embedding de la question
        query_embedding = self.embedding_service.embed_text(query)

        # Construire le filtre (avec support du doc_type)
        filter_dict = self.build_filter(crypto=crypto, doc_type=doc_type)

        # Recherche dans Pinecone
        results = self.pinecone_service.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict
        )

        # Filtrer par score minimum
        filtered_results = [
            r for r in results
            if r["score"] >= self.min_score
        ]

        logger.info(f"✓ Trouvé {len(filtered_results)}/{len(results)} résultats")

        return filtered_results

    def retrieve_with_context(self, query, top_k=5):
        """
        ✅ AMÉLIORÉ: Adapte la recherche selon le type de question
        """
        # ✅ Détecter le type
        query_type = self.detect_query_type(query)
        crypto = self.extract_crypto_from_query(query)
        
        logger.info(f"🤖 Mode {query_type.upper()}: Recherche adaptée")
        
        # ✅ Adapter la recherche par type
        if query_type == "price":
            # Priorité aux documents de prix
            documents = self.retrieve(
                query, 
                top_k=top_k, 
                crypto=crypto,
                doc_type="price"
            )
        
        elif query_type == "sentiment":
            # Priorité aux posts
            documents = self.retrieve(
                query,
                top_k=top_k,
                crypto=crypto,
                doc_type="post"
            )
        
        else:  # general ou analysis
            # Recherche sans restriction de type
            documents = self.retrieve(query, top_k=top_k, crypto=crypto)

        # Formater le contexte
        context_parts = []
        for i, doc in enumerate(documents):
            doc_type = doc['metadata'].get('type', 'unknown')
            
            part = (
                f"[Document {i+1}] (Type: {doc_type})\n"
                f"Crypto: {doc['metadata'].get('crypto', 'UNKNOWN')}\n"
                f"Date: {doc['metadata'].get('date', 'N/A')}\n"
                f"Score: {doc['score']:.3f}\n"
                f"Contenu: {doc['text']}\n"
            )
            
            context_parts.append(part)

        context = "\n---\n".join(context_parts)

        result = {
            "query": query,
            "query_type": query_type,  # ✅ NOUVEAU: Inclure le type
            "documents": documents,
            "context": context,
            "num_results": len(documents),
        }

        logger.info(f"Contexte formaté: {len(documents)} documents")
        return result

    def retrieve_by_types(self, query, doc_types, top_k_per_type=2):
        """
        Recherche dans plusieurs types de documents
        """
        self._init_services()

        all_results = []
        query_embedding = self.embedding_service.embed_text(query)

        logger.info(f"🔍 Recherche par types: {doc_types}")

        for doc_type in doc_types:
            filter_dict = self.build_filter(doc_type=doc_type)
            
            results = self.pinecone_service.search(
                query_embedding=query_embedding,
                top_k=top_k_per_type,
                filter_dict=filter_dict
            )
            
            all_results.extend(results)

        # Trier par score décroissant
        all_results.sort(key=lambda x: x["score"], reverse=True)

        logger.info(f"✓ Total: {len(all_results)} résultats")
        return all_results

    def retrieve_by_date_range(self, query, start_date=None, end_date=None, top_k=None):
        """
        Recherche avec filtre de plage de dates
        """
        self._init_services()

        top_k = top_k or self.default_top_k
        query_embedding = self.embedding_service.embed_text(query)

        # Construire le filtre de date
        filter_dict = {}
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            filter_dict["date"] = date_filter

        logger.info(f"🔍 Recherche par date: {start_date} à {end_date}")

        results = self.pinecone_service.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict if filter_dict else None
        )

        logger.info(f"✓ Trouvé {len(results)} résultats")
        return results

    def retrieve_by_crypto_and_type(self, query, crypto, doc_types, top_k=None):
        """
        Recherche avec filtres de crypto ET type de document
        """
        self._init_services()

        top_k = top_k or self.default_top_k
        query_embedding = self.embedding_service.embed_text(query)

        all_results = []

        for doc_type in doc_types:
            filter_dict = self.build_filter(crypto=crypto, doc_type=doc_type)
            
            results = self.pinecone_service.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_dict=filter_dict
            )
            
            all_results.extend(results)

        # Trier par score décroissant
        all_results.sort(key=lambda x: x["score"], reverse=True)

        logger.info(f"✓ Trouvé {len(all_results)} résultats")
        return all_results


# =====================================================================
# SINGLETON GLOBAL
# =====================================================================
_retriever_service = None


def get_retriever_service():
    """
    Retourne une instance unique du service de retrieval (singleton)
    """
    global _retriever_service
    
    if _retriever_service is None:
        _retriever_service = RetrieverService()
        logger.info("✓ Singleton RetrieverService créé")
    
    return _retriever_service