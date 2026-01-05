"""
Interface avec Pinecone pour stocker et rechercher les vecteurs.
"""

import time
from pinecone import Pinecone, ServerlessSpec

from app.rag.config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD,
    PINECONE_REGION,
    EMBEDDING_DIMENSION
)
from app.rag.logger import get_logger

logger = get_logger("pinecone_service")


class PineconeService:
    """Service pour interagir avec Pinecone"""

    def __init__(self, api_key=PINECONE_API_KEY, index_name=PINECONE_INDEX_NAME):
        """
        Initialise le service Pinecone
        
        Args:
            api_key (str): Clé API Pinecone
            index_name (str): Nom de l'index
        """
        self.api_key = api_key
        self.index_name = index_name
        self.dimension = EMBEDDING_DIMENSION
        self.client = None
        self.index = None
        logger.info(f"PineconeService initialisé: {index_name}")

    def connect(self):
        """
        Établit la connexion à Pinecone et crée l'index s'il n'existe pas
        """
        logger.info("📡 Connexion à Pinecone...")
        
        try:
            # Créer le client Pinecone
            self.client = Pinecone(api_key=self.api_key)
            
            # Lister les index existants
            existing_indexes = [idx.name for idx in self.client.list_indexes()]
            logger.info(f"Index existants: {existing_indexes}")
            
            # Créer l'index s'il n'existe pas
            if self.index_name not in existing_indexes:
                logger.info(f"🔨 Création de l'index {self.index_name}...")
                self.client.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=PINECONE_CLOUD,
                        region=PINECONE_REGION
                    )
                )
                logger.info("Attente de la création de l'index (10s)...")
                time.sleep(10)  # Attendre la création
            
            # Se connecter à l'index
            self.index = self.client.Index(self.index_name)
            logger.info(f"✓ Connecté à l'index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur de connexion à Pinecone: {e}")
            raise

    def upsert_chunks(self, chunks, batch_size=100):
        """
        Indexe les chunks avec leurs embeddings dans Pinecone
        
        Args:
            chunks (list): Chunks avec embeddings
            batch_size (int): Taille des batches pour l'indexation
            
        Returns:
            int: Nombre de vecteurs indexés
        """
        if self.index is None:
            self.connect()
        
        if not chunks:
            logger.warning("Aucun chunk à indexer")
            return 0
        
        # DEBUG: Afficher le premier chunk
        logger.info(f"DEBUG - Nombre de chunks: {len(chunks)}")
        if chunks:
            first_chunk = chunks[0]
            logger.info(f"DEBUG - Premier chunk keys: {list(first_chunk.keys())}")
            logger.info(f"DEBUG - Premier chunk type: {first_chunk.get('type')}")
            logger.info(f"DEBUG - Premier chunk embedding length: {len(first_chunk.get('embedding', []))}")
            logger.info(f"DEBUG - Premier chunk text preview: {first_chunk.get('text', '')[:100]}")
        
        # PRÉPARER LES VECTEURS AVEC LE NOUVEAU FORMAT PINCECONE V3+
        vectors = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = chunk.get("id", f"chunk_{i}")
            embedding = chunk.get("embedding", [])
            
            # Vérifier l'embedding
            if not embedding:
                logger.warning(f"Chunk {chunk_id} n'a pas d'embedding")
                continue
            
            if len(embedding) != self.dimension:
                logger.warning(f"Chunk {chunk_id} a une dimension incorrecte: {len(embedding)} != {self.dimension}")
                continue
            
            # Récupérer les métadonnées
            metadata = chunk.get("metadata", {})
            
            # Créer les métadonnées pour Pinecone
            pinecone_metadata = {
                "type": chunk.get("type", "unknown"),
                "crypto": chunk.get("crypto", "UNKNOWN"),
                "date": chunk.get("date", ""),
                "source": chunk.get("source", "system"),
                "text": chunk.get("text", "")[:1000],  # Tronquer à 1000 caractères
                "sentiment_score": metadata.get("sentiment_score"),
                "sentiment_label": metadata.get("sentiment_label"),
                "price_change": metadata.get("price_change"),
                "pearson_r": metadata.get("pearson_r"),
                "p_value": metadata.get("p_value"),
                "lag_hours": metadata.get("lag_hours"),
                "chunk_index": chunk.get("chunk_index"),
            }
            
            # Nettoyer les métadonnées (enlever les valeurs None)
            pinecone_metadata = {k: v for k, v in pinecone_metadata.items() if v is not None}
            
            # FORMAT CORRECT POUR PINECONE V3+: (id, vector, metadata)
            vectors.append((
                str(chunk_id),      # id (doit être string)
                embedding,          # vector (liste de floats)
                pinecone_metadata   # metadata (dict)
            ))
        
        logger.info(f"✅ {len(vectors)} vecteurs préparés pour Pinecone")
        
        if not vectors:
            logger.error("❌ Aucun vecteur valide à indexer!")
            return 0
        
        # UPSERT PAR BATCHES
        total = len(vectors)
        total_upserted = 0
        
        logger.info(f"🔄 Indexation de {total} vecteurs (batch_size={batch_size})...")
        
        try:
            for i in range(0, total, batch_size):
                batch = vectors[i:i + batch_size]
                
                # DEBUG: Afficher le premier vecteur du batch
                if i == 0:
                    first_vector = batch[0]
                    logger.info(f"DEBUG - Format du premier vecteur: {type(first_vector)}")
                    logger.info(f"DEBUG - ID: {first_vector[0]}")
                    logger.info(f"DEBUG - Vector length: {len(first_vector[1])}")
                    logger.info(f"DEBUG - Metadata keys: {list(first_vector[2].keys())}")
                
                # UPSERT avec le format correct
                self.index.upsert(vectors=batch)
                total_upserted += len(batch)
                
                # Log progression
                percent = (total_upserted / total) * 100
                if i % (batch_size * 10) == 0 or i + batch_size >= total:
                    logger.info(f"   Indexation: {total_upserted}/{total} ({percent:.1f}%)")
            
            logger.info(f"✅ Indexation terminée: {total_upserted} vecteurs indexés")
            
            # VÉRIFICATION IMMÉDIATE
            time.sleep(2)  # Petite pause pour la synchronisation
            try:
                stats = self.index.describe_index_stats()
                logger.info(f"✅ VÉRIFICATION - Vecteurs dans Pinecone: {stats.total_vector_count}")
            except Exception as e:
                logger.error(f"Erreur vérification stats: {e}")
            
            return total_upserted
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'indexation: {e}")
            # Afficher plus de détails sur l'erreur
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    def search(self, query_embedding, top_k=5, filter_dict=None):
        """
        Recherche les documents similaires dans Pinecone
        
        Args:
            query_embedding (list): Vecteur de requête (384 floats)
            top_k (int): Nombre de résultats (défaut: 5)
            filter_dict (dict): Filtre optionnel pour les métadonnées
            
        Returns:
            list: Résultats avec scores de similarité
        """
        if self.index is None:
            self.connect()
        
        try:
            # Paramètres de recherche
            query_params = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True,
            }
            
            # Ajouter le filtre si fourni
            if filter_dict:
                query_params["filter"] = filter_dict
                logger.debug(f"Recherche avec filtre: {filter_dict}")
            
            # Exécuter la recherche
            results = self.index.query(**query_params)
            
            # Formater les résultats
            output = []
            for match in results.matches:
                result = {
                    "id": match.id,
                    "score": float(match.score),
                    "text": match.metadata.get("text", ""),
                    "metadata": dict(match.metadata) if match.metadata else {},
                }
                output.append(result)
            
            logger.debug(f"Recherche retourné {len(output)} résultats (top_k={top_k})")
            return output
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la recherche: {e}")
            raise

    def delete_all(self):
        """Supprime tous les vecteurs de l'index"""
        if self.index is None:
            self.connect()
        
        try:
            self.index.delete(delete_all=True)
            logger.info("✓ Tous les vecteurs supprimés")
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de la suppression: {e}")

    def delete_by_filter(self, filter_dict):
        """
        Supprime les vecteurs correspondant à un filtre
        
        Args:
            filter_dict (dict): Filtre pour les métadonnées
        """
        if self.index is None:
            self.connect()
        
        try:
            self.index.delete(filter=filter_dict)
            logger.info(f"✓ Vecteurs supprimés avec filtre: {filter_dict}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression: {e}")
            raise

    def get_stats(self):
        """
        Retourne les statistiques de l'index
        
        Returns:
            dict: Informations sur l'index
        """
        if self.index is None:
            self.connect()
        
        try:
            stats = self.index.describe_index_stats()
            
            info = {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {},
                "index_name": self.index_name,
            }
            
            logger.info(f"Statistiques index: {stats.total_vector_count} vecteurs")
            return info
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des stats: {e}")
            raise

    def describe_index(self):
        """
        Retourne les détails de l'index
        
        Returns:
            dict: Détails de l'index
        """
        if self.client is None:
            self.connect()
        
        try:
            index_info = self.client.describe_index(self.index_name)
            logger.info(f"Description index: {index_info}")
            return index_info
        except Exception as e:
            logger.error(f"❌ Erreur lors de la description: {e}")
            raise


# =====================================================================
# SINGLETON GLOBAL
# =====================================================================
_pinecone_service = None


def get_pinecone_service(api_key=PINECONE_API_KEY, index_name=PINECONE_INDEX_NAME):
    """
    Retourne une instance unique du service Pinecone (singleton)
    
    Args:
        api_key (str): Clé API (ignorée si service déjà créé)
        index_name (str): Nom de l'index (ignoré si service déjà créé)
        
    Returns:
        PineconeService: Instance unique du service
        
    Exemple:
        service = get_pinecone_service()
        results = service.search(query_embedding, top_k=5)
    """
    global _pinecone_service
    
    if _pinecone_service is None:
        _pinecone_service = PineconeService(api_key, index_name)
        _pinecone_service.connect()
        logger.info("✓ Singleton PineconeService créé et connecté")
    
    return _pinecone_service