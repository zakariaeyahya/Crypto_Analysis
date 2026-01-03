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


def print_separator(title=""):
    """Affiche une ligne de séparation"""
    sep = "=" * 70
    if title:
        print(f"\n{sep}")
        print(f"  {title}")
        print(f"{sep}\n")
    else:
        print(f"\n{sep}\n")


def run_indexation(clear_before=False):
    """
    Exécute le pipeline d'indexation complet
    
    Args:
        clear_before (bool): Supprimer l'index avant réindexation
    """
    start_time = time.time()

    print_separator("INDEXATION RAG - CRYPTO SENTIMENT")

    # =====================================================================
    # ETAPE 1: CHARGER LES DOCUMENTS
    # =====================================================================
    print("📚 [1/5] Chargement des documents...")
    logger.info("Début du chargement des documents")

    try:
        loader = DocumentLoader()
        documents = loader.load_all()

        if not documents:
            logger.error("Aucun document chargé!")
            print("ERREUR: Aucun document chargé!")
            return False

        stats = loader.get_stats()
        print(f" {len(documents)} documents chargés")
        print(f"   Répartition:")
        for doc_type, count in stats.items():
            print(f"      - {doc_type}: {count}")

    except Exception as e:
        logger.error(f"Erreur chargement documents: {e}")
        print(f"ERREUR: {e}")
        return False

    # =====================================================================
    # ETAPE 2: DÉCOUPER EN CHUNKS
    # =====================================================================
    print("\n  [2/5] Découpage en chunks...")
    logger.info("Début du chunking")

    try:
        chunker = DocumentChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk_all(documents)

        if not chunks:
            logger.error(" Aucun chunk créé!")
            print(" ERREUR: Aucun chunk créé!")
            return False

        stats = chunker.get_stats(chunks)
        print(f"   {stats['total_chunks']} chunks créés")
        print(f"   Taille moyenne: {stats['avg_length']:.0f} caractères")
        print(f"   Min: {stats['min_length']}, Max: {stats['max_length']}")
        print(f"   Par type:")
        for doc_type, count in stats['by_type'].items():
            print(f"      - {doc_type}: {count} chunks")

    except Exception as e:
        logger.error(f" Erreur chunking: {e}")
        print(f"ERREUR: {e}")
        return False

    # =====================================================================
    # ETAPE 3: GÉNÉRER LES EMBEDDINGS
    # =====================================================================
    print("\n[3/5] Génération des embeddings...")
    logger.info("Début de la génération des embeddings")

    try:
        embedding_service = get_embedding_service()
        chunks_with_embeddings = embedding_service.embed_chunks(
            chunks,
            show_progress=True
        )

        print(f"   ✓ {len(chunks_with_embeddings)} embeddings générés")
        print(f"   Dimension: {embedding_service.get_dimension()}")

    except Exception as e:
        logger.error(f"Erreur embeddings: {e}")
        print(f"ERREUR: {e}")
        return False

    # =====================================================================
    # ETAPE 4: CONNEXION À PINECONE
    # =====================================================================
    print("\n🔌 [4/5] Connexion à Pinecone...")
    logger.info("Connexion à Pinecone")

    try:
        pinecone_service = get_pinecone_service()
        logger.info(" Connecté à Pinecone")
        print("    Connecté à Pinecone")

    except Exception as e:
        logger.error(f" Erreur connexion Pinecone: {e}")
        print(f" ERREUR: {e}")
        return False

    # =====================================================================
    # ETAPE 4b: SUPPRIMER ANCIENS VECTEURS SI DEMANDÉ
    # =====================================================================
    if clear_before:
        print("\n🗑️  Suppression des anciens vecteurs...")
        logger.warning("Suppression de l'index existant")

        try:
            pinecone_service.delete_all()
            logger.info("✓ Index supprimé")
            print("   ✓ Index supprimé")
            time.sleep(2)  # Attendre la suppression

        except Exception as e:
            logger.error(f" Erreur suppression: {e}")
            print(f"ERREUR: {e}")
            return False

    # =====================================================================
    # ETAPE 5: INDEXATION DANS PINECONE
    # =====================================================================
    print("\n [5/5] Indexation dans Pinecone...")
    logger.info("Début de l'indexation")

    try:
        num_indexed = pinecone_service.upsert_chunks(
            chunks=chunks_with_embeddings,
            batch_size=100
        )

        print(f"   ✓ {num_indexed} vecteurs indexés")

    except Exception as e:
        logger.error(f"Erreur indexation: {e}")
        print(f"ERREUR: {e}")
        return False

    # =====================================================================
    # STATS FINALES
    # =====================================================================
    time.sleep(2)  # Attendre la synchronisation Pinecone

    try:
        stats = pinecone_service.get_stats()
        duration = time.time() - start_time

        print_separator(" INDEXATION TERMINÉE")
        print(f"  Total vecteurs: {stats['total_vectors']}")
        print(f"  Dimension: {stats['dimension']}")
        print(f"  Durée: {duration:.2f} secondes")

        if stats.get('namespaces'):
            print(f"  Namespaces: {stats['namespaces']}")

        logger.info(f"✓ Indexation réussie: {stats['total_vectors']} vecteurs")
        return True

    except Exception as e:
        logger.error(f"Erreur récupération stats: {e}")
        print(f" ERREUR: {e}")
        return False


def test_search():
    """
    Teste la recherche après indexation
    """
    print_separator(" TEST DE RECHERCHE")

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

        logger.info("Début des tests de recherche")

        for query in test_queries:
            print(f"\n🔍 Query: \"{query}\"")
            logger.info(f"Test query: {query}")

            try:
                # Générer l'embedding de la requête
                query_embedding = embedding_service.embed_text(query)

                # Rechercher dans Pinecone
                results = pinecone_service.search(
                    query_embedding=query_embedding,
                    top_k=3
                )

                print(f"   Résultats: {len(results)}")

                if not results:
                    print("  Aucun résultat trouvé")
                    continue

                for i, result in enumerate(results, 1):
                    print(f"\n   [{i}] Score: {result['score']:.4f}")
                    print(f"       Type: {result['metadata'].get('type', 'unknown')}")
                    print(f"       Crypto: {result['metadata'].get('crypto', 'UNKNOWN')}")
                    print(f"       Date: {result['metadata'].get('date', 'N/A')}")
                    text_preview = result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
                    print(f"       Texte: {text_preview}")

            except Exception as e:
                logger.error(f"Erreur test query: {e}")
                print(f"   ERREUR: {e}")
                continue

        logger.info("✓ Tests de recherche terminés")
        print_separator("TESTS TERMINÉS")
        return True

    except Exception as e:
        logger.error(f" Erreur test search: {e}")
        print(f"\n ERREUR: {e}")
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
                print("\n")
                test_search()

        # Code de sortie
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.warning("Indexation annulée par l'utilisateur")
        print("\n\n⚠️  Indexation annulée par l'utilisateur")
        sys.exit(1)

    except Exception as e:
        logger.error(f" Erreur fatale: {e}")
        print(f"\nERREUR FATALE: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()