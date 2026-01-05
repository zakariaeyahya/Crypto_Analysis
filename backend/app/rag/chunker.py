"""
Découpe les documents longs en morceaux plus petits (chunks) pour une meilleure
précision de recherche.
"""

import re
import copy
from app.rag.logger import get_logger

logger = get_logger("chunker")


class DocumentChunker:
    """Découpe les documents en chunks optimisés pour la recherche"""

    def __init__(self, chunk_size=500, overlap=50):
        """
        Initialise le chunker
        
        Args:
            chunk_size (int): Taille maximale d'un chunk en caractères (défaut: 500)
            overlap (int): Chevauchement entre chunks en mots (défaut: 50)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        logger.info(f"DocumentChunker initialisé: chunk_size={chunk_size}, overlap={overlap}")

    def _split_into_sentences(self, text):
        """
        Découpe le texte en phrases
        
        Args:
            text (str): Texte à découper
            
        Returns:
            list: Liste des phrases
        """
        # Pattern pour découper après . ! ? suivi d'un espace
        pattern = r'(?<=[.!?])\s+'
        sentences = re.split(pattern, text)
        # Filtrer les phrases vides
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def chunk_document(self, doc):
        """
        Découpe un document en chunks
        
        Args:
            doc (dict): Document à découper
            
        Returns:
            list: Liste des chunks du document
        """
        text = doc.get("text", "")
        
        # Si texte court, pas de découpage nécessaire
        if len(text) <= self.chunk_size:
            chunk = copy.deepcopy(doc)
            chunk["id"] = f"{doc['id']}_0"
            logger.debug(f"Document court: {doc['id']} ({len(text)} caractères)")
            return [chunk]
        
        # Sinon, découper en phrases puis regrouper
        sentences = self._split_into_sentences(text)
        chunks = []
        current_chunk = ""
        chunk_index = 0

        for sentence in sentences:
            # Si ajouter la phrase dépasse la taille max
            if len(current_chunk) + len(sentence) + 1 > self.chunk_size:
                # Sauvegarder le chunk actuel s'il n'est pas vide
                if current_chunk.strip():
                    chunk = copy.deepcopy(doc)
                    chunk["id"] = f"{doc['id']}_{chunk_index}"
                    chunk["text"] = current_chunk.strip()
                    chunk["chunk_index"] = chunk_index
                    chunks.append(chunk)
                    logger.debug(f"Chunk créé: {chunk['id']} ({len(current_chunk)} caractères)")
                    chunk_index += 1

                # Nouveau chunk avec overlap (derniers mots du chunk précédent)
                words = current_chunk.split()
                overlap_text = " ".join(words[-10:]) if len(words) > 10 else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                # Ajouter la phrase au chunk courant
                current_chunk += " " + sentence if current_chunk else sentence

        # Sauvegarder le dernier chunk
        if current_chunk.strip():
            chunk = copy.deepcopy(doc)
            chunk["id"] = f"{doc['id']}_{chunk_index}"
            chunk["text"] = current_chunk.strip()
            chunk["chunk_index"] = chunk_index
            chunks.append(chunk)
            logger.debug(f"Chunk créé (dernier): {chunk['id']} ({len(current_chunk)} caractères)")

        logger.info(f"Document {doc['id']} découpé en {len(chunks)} chunks")
        return chunks

    def chunk_all(self, documents):
        """
        Découpe tous les documents
        
        Args:
            documents (list): Liste des documents à découper
            
        Returns:
            list: Liste de tous les chunks
        """
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        
        logger.info(f"✓ Créé {len(all_chunks)} chunks à partir de {len(documents)} documents")
        return all_chunks

    def get_stats(self, chunks):
        """
        Retourne les statistiques des chunks
        
        Args:
            chunks (list): Liste des chunks
            
        Returns:
            dict: Statistiques (total, longueur moyenne, par type)
        """
        if not chunks:
            logger.warning("Aucun chunk à analyser")
            return {
                "total_chunks": 0,
                "avg_length": 0,
                "by_type": {}
            }

        total = len(chunks)
        lengths = [len(c.get("text", "")) for c in chunks]
        avg_length = sum(lengths) / total if total > 0 else 0
        min_length = min(lengths) if lengths else 0
        max_length = max(lengths) if lengths else 0

        # Compter par type de document
        by_type = {}
        for chunk in chunks:
            doc_type = chunk.get("type", "unknown")
            by_type[doc_type] = by_type.get(doc_type, 0) + 1

        stats = {
            "total_chunks": total,
            "avg_length": round(avg_length, 2),
            "min_length": min_length,
            "max_length": max_length,
            "by_type": by_type,
        }

        logger.info(f"Statistiques chunks: {stats}")
        return stats

    def display_stats(self, chunks):
        """
        Affiche les statistiques de manière lisible

        Args:
            chunks (list): Liste des chunks
        """
        stats = self.get_stats(chunks)

        logger.info("=" * 60)
        logger.info("STATISTIQUES DES CHUNKS")
        logger.info("=" * 60)
        logger.info(f"Total chunks:        {stats['total_chunks']}")
        logger.info(f"Longueur moyenne:    {stats['avg_length']:.0f} caracteres")
        logger.info(f"Longueur min:        {stats['min_length']} caracteres")
        logger.info(f"Longueur max:        {stats['max_length']} caracteres")
        logger.info("Par type de document:")
        for doc_type, count in stats['by_type'].items():
            logger.info(f"  - {doc_type}: {count} chunks")
        logger.info("=" * 60)