import sys
import time
import argparse
from pathlib import Path

# Ajouter backend au path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.rag.document_loader import DocumentLoader
from app.rag.chunker import DocumentChunker
from app.rag.embedding_service import get_embedding_service
from app.rag.pinecone_service import get_pinecone_service
from app.rag.logger import get_logger

logger = get_logger("index_documents")


def log_separator(title=""):
    """Affiche une ligne de séparation"""
    sep = "=" * 70
    if title:
        logger.info(sep)
        logger.info(f"  {title}")
        logger.info(sep)
    else:
        logger.info(sep)


def run_indexation(clear_before=False):
    """
    Exécute le pipeline d'indexation complet
    
    Args:
        clear_before (bool): Supprimer l'index avant réindexation
    """
    start_time = time.time()

    log_separator("INDEXATION RAG - CRYPTO SENTIMENT")

    # =====================================================================
    # ETAPE 1: CHARGER LES DOCUMENTS
    # =====================================================================
    logger.info("[1/5] Chargement des documents...")

    try:
        loader = DocumentLoader()
        documents = loader.load_all()

        if not documents:
            logger.error("Aucun document charge!")
            return False

        stats = loader.get_stats()
        logger.info(f"{len(documents)} documents charges")
        logger.info("Repartition:")
        for doc_type, count in stats.items():
            logger.info(f"   - {doc_type}: {count}")

    except Exception as e:
        logger.error(f"Erreur chargement documents: {e}")
        return False

    # =====================================================================
    # ETAPE 2: DÉCOUPER EN CHUNKS
    # =====================================================================
    logger.info("[2/5] Decoupage en chunks...")

    try:
        chunker = DocumentChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk_all(documents)

        if not chunks:
            logger.error("Aucun chunk cree!")
            return False

        stats = chunker.get_stats(chunks)
        logger.info(f"{stats['total_chunks']} chunks crees")
        logger.info(f"Taille moyenne: {stats['avg_length']:.0f} caracteres")
        logger.info(f"Min: {stats['min_length']}, Max: {stats['max_length']}")
        logger.info("Par type:")
        for doc_type, count in stats['by_type'].items():
            logger.info(f"   - {doc_type}: {count} chunks")

    except Exception as e:
        logger.error(f"Erreur chunking: {e}")
        return False

    # =====================================================================
    # ETAPE 3: GÉNÉRER LES EMBEDDINGS
    # =====================================================================
    logger.info("[3/5] Generation des embeddings...")

    try:
        embedding_service = get_embedding_service()
        chunks_with_embeddings = embedding_service.embed_chunks(
            chunks,
            show_progress=True
        )

        logger.info(f"{len(chunks_with_embeddings)} embeddings generes")
        logger.info(f"Dimension: {embedding_service.get_dimension()}")

    except Exception as e:
        logger.error(f"Erreur embeddings: {e}")
        return False

    # =====================================================================
    # ETAPE 4: CONNEXION À PINECONE
    # =====================================================================
    logger.info("[4/5] Connexion a Pinecone...")

    try:
        pinecone_service = get_pinecone_service()
        logger.info("Connecte a Pinecone")

    except Exception as e:
        logger.error(f"Erreur connexion Pinecone: {e}")
        return False

    # =====================================================================
    # ETAPE 4b: SUPPRIMER ANCIENS VECTEURS SI DEMANDÉ
    # =====================================================================
    if clear_before:
        logger.warning("Suppression des anciens vecteurs...")

        try:
            pinecone_service.delete_all()
            logger.info("Index supprime")
            time.sleep(2)  # Attendre la suppression

        except Exception as e:
            logger.error(f"Erreur suppression: {e}")
            return False

    # =====================================================================
    # ETAPE 5: INDEXATION DANS PINECONE
    # =====================================================================
    logger.info("[5/5] Indexation dans Pinecone...")

    try:
        num_indexed = pinecone_service.upsert_chunks(
            chunks=chunks_with_embeddings,
            batch_size=100
        )

        logger.info(f"{num_indexed} vecteurs indexes")

    except Exception as e:
        logger.error(f"Erreur indexation: {e}")
        return False

    # =====================================================================
    # STATS FINALES
    # =====================================================================
    time.sleep(2)  # Attendre la synchronisation Pinecone

    try:
        stats = pinecone_service.get_stats()
        duration = time.time() - start_time

        log_separator("INDEXATION TERMINEE")
        logger.info(f"Total vecteurs: {stats['total_vectors']}")
        logger.info(f"Dimension: {stats['dimension']}")
        logger.info(f"Duree: {duration:.2f} secondes")

        if stats.get('namespaces'):
            logger.info(f"Namespaces: {stats['namespaces']}")

        logger.info(f"Indexation reussie: {stats['total_vectors']} vecteurs")
        return True

    except Exception as e:
        logger.error(f"Erreur recuperation stats: {e}")
        return False


def test_search():
    """
    Teste la recherche après indexation
    """
    log_separator("TEST DE RECHERCHE")

    try:
        embedding_service = get_embedding_service()
        pinecone_service = get_pinecone_service()

        test_queries = [
            "Quel est le sentiment de Bitcoin?",
            "Comment évolue Ethereum?",
            "Corrélation prix sentiment Solana",
            "Posts récents sur Bitcoin",
            "Analyse sentiment crypto",
        ]

        logger.info("Debut des tests de recherche")

        for query in test_queries:
            logger.info(f"Query: \"{query}\"")

            try:
                # Générer l'embedding de la requête
                query_embedding = embedding_service.embed_text(query)

                # Rechercher dans Pinecone
                results = pinecone_service.search(
                    query_embedding=query_embedding,
                    top_k=3
                )

                logger.info(f"Resultats: {len(results)}")

                if not results:
                    logger.warning("Aucun resultat trouve")
                    continue

                for i, result in enumerate(results, 1):
                    logger.info(f"[{i}] Score: {result['score']:.4f}")
                    logger.info(f"    Type: {result['metadata'].get('type', 'unknown')}")
                    logger.info(f"    Crypto: {result['metadata'].get('crypto', 'UNKNOWN')}")
                    logger.info(f"    Date: {result['metadata'].get('date', 'N/A')}")
                    text_preview = result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
                    logger.info(f"    Texte: {text_preview}")

            except Exception as e:
                logger.error(f"Erreur test query: {e}")
                continue

        logger.info("Tests de recherche termines")
        log_separator("TESTS TERMINES")
        return True

    except Exception as e:
        logger.error(f"Erreur test search: {e}")
        return False


def main():
    """
    Fonction principale avec arguments CLI
    """
    parser = argparse.ArgumentParser(
        description="Indexation RAG - Charge et indexe les documents dans Pinecone",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python scripts/index_documents.py              # Indexation normale
  python scripts/index_documents.py --clear      # Supprimer + réindexer
  python scripts/index_documents.py --test       # Indexer + tester
  python scripts/index_documents.py --test-only  # Tester seulement
        """
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        help="Supprimer l'index existant avant réindexation"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Exécuter les tests après indexation"
    )

    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Exécuter uniquement les tests (pas d'indexation)"
    )

    args = parser.parse_args()

    # =====================================================================
    # EXÉCUTION
    # =====================================================================
    try:
        if args.test_only:
            # Mode test seulement
            success = test_search()

        else:
            # Mode indexation
            success = run_indexation(clear_before=args.clear)

            # Tests après indexation si demandé
            if success and args.test:
                test_search()

        # Code de sortie
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.warning("Indexation annulee par l'utilisateur")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()