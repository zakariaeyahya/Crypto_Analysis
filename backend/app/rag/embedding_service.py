"""
Convertit le texte en vecteurs numériques (embeddings) de dimension 384.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

from app.rag.config import EMBEDDING_MODEL, EMBEDDING_DIMENSION
from app.rag.logger import get_logger

logger = get_logger("embedding_service")


class EmbeddingService:
    """Service pour générer des embeddings de texte"""

    def __init__(self, model_name=EMBEDDING_MODEL):
        """
        Initialise le service d'embedding
        
        Args:
            model_name (str): Nom du modèle SentenceTransformer (défaut: all-MiniLM-L6-v2)
        """
        self.model_name = model_name
        self.dimension = EMBEDDING_DIMENSION
        self.model = None  # Lazy loading - charger uniquement à la première utilisation
        self.batch_size = 64  # Taille des batches (augmenter si GPU disponible)
        logger.info(f"EmbeddingService initialisé: {model_name} (dim={EMBEDDING_DIMENSION})")

    def _load_model(self):
        """Charge le modèle une seule fois (lazy loading)"""
        if self.model is None:
            logger.info(f"📥 Chargement du modèle {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✓ Modèle chargé: {self.model_name}")

    def embed_text(self, text, normalize=True):
        """
        Génère l'embedding d'un seul texte
        
        Args:
            text (str): Texte à encoder
            normalize (bool): Normaliser le vecteur (défaut: True)
            
        Returns:
            list: Vecteur de 384 floats
        """
        self._load_model()
        
        # Encoder le texte
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        # Normaliser si demandé
        if normalize:
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
        
        return embedding.tolist()

    def embed_texts_batch(self, texts, normalize=True):
        """
        Génère les embeddings d'une liste de textes
        
        Args:
            texts (list): Liste de textes à encoder
            normalize (bool): Normaliser les vecteurs (défaut: True)
            
        Returns:
            list: Liste de vecteurs (chacun une liste de 384 floats)
        """
        self._load_model()
        
        if not texts:
            return []
        
        # Encoding par batch (plus rapide qu'un à un)
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            batch_size=self.batch_size,
            show_progress_bar=False
        )
        
        # Normaliser si demandé
        if normalize:
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Éviter division par zéro
            embeddings = embeddings / norms
        
        return embeddings.tolist()

    def embed_chunks(self, chunks, show_progress=True):
        """
        Ajoute les embeddings à chaque chunk
        
        Args:
            chunks (list): Liste des chunks à encoder
            show_progress (bool): Afficher la progression (défaut: True)
            
        Returns:
            list: Chunks avec le champ "embedding" ajouté
        """
        texts = [chunk.get("text", "") for chunk in chunks]
        total = len(texts)
        
        if total == 0:
            logger.warning("Aucun chunk à encoder")
            return chunks
        
        logger.info(f"🔄 Génération de {total} embeddings...")
        
        # Traiter par batches avec logging de progression
        all_embeddings = []
        for i in range(0, total, self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_embeddings = self.embed_texts_batch(batch_texts, normalize=True)
            all_embeddings.extend(batch_embeddings)
            
            # Log progression
            if show_progress:
                progress = min(i + self.batch_size, total)
                percent = (progress / total) * 100
                logger.info(f"   Embeddings: {progress}/{total} ({percent:.1f}%)")
        
        # Ajouter embedding à chaque chunk
        for chunk, embedding in zip(chunks, all_embeddings):
            chunk["embedding"] = embedding
        
        logger.info(f"✓ {total} embeddings générés avec succès")
        return chunks

    def get_dimension(self):
        """
        Retourne la dimension des embeddings
        
        Returns:
            int: Dimension (384)
        """
        return self.dimension

    def get_model_info(self):
        """
        Retourne les informations du modèle
        
        Returns:
            dict: Infos du modèle
        """
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "batch_size": self.batch_size,
            "loaded": self.model is not None
        }


# =====================================================================
# SINGLETON GLOBAL
# =====================================================================
_embedding_service = None


def get_embedding_service(model_name=EMBEDDING_MODEL):
    """
    Retourne une instance unique du service d'embedding (singleton)
    
    Args:
        model_name (str): Nom du modèle (ignoré si service déjà créé)
        
    Returns:
        EmbeddingService: Instance unique du service
        
    Exemple:
        service = get_embedding_service()
        embeddings = service.embed_texts_batch(["texte1", "texte2"])
    """
    global _embedding_service
    
    if _embedding_service is None:
        _embedding_service = EmbeddingService(model_name)
        logger.info("✓ Singleton EmbeddingService créé")
    
    return _embedding_service