"""
Test du service Pinecone
Vérifie la connexion et les opérations sur l'index vectoriel.
"""

import sys
from pathlib import Path

# Ajouter backend au path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_pinecone():
    """Test du PineconeService"""
    print("=" * 60)
    print("TEST PINECONE SERVICE")
    print("=" * 60)

    from app.rag.config import PINECONE_API_KEY, PINECONE_INDEX_NAME

    results = []

    # Vérifier la clé API
    print("\n[1] Vérification de la clé API")
    if not PINECONE_API_KEY:
        print("    ERREUR: PINECONE_API_KEY non défini dans .env")
        results.append(("api_key", False))
        return False
    else:
        print(f"    Clé API: {'*' * 10}...{PINECONE_API_KEY[-4:]}")
        print(f"    Index: {PINECONE_INDEX_NAME}")
        results.append(("api_key", True))

    # Test connexion
    print("\n[2] Test connexion à Pinecone")
    try:
        from app.rag.pinecone_service import get_pinecone_service

        service = get_pinecone_service()
        print("    Connexion établie!")
        results.append(("connection", True))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("connection", False))
        return False

    # Test get_stats
    print("\n[3] Test get_stats()")
    try:
        stats = service.get_stats()
        print(f"    Total vecteurs: {stats['total_vectors']}")
        print(f"    Dimension: {stats['dimension']}")
        print(f"    Index: {stats['index_name']}")
        results.append(("get_stats", True))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("get_stats", False))

    # Test search (si index non vide)
    print("\n[4] Test search()")
    try:
        from app.rag.embedding_service import get_embedding_service

        embedding_service = get_embedding_service()
        query = "Bitcoin sentiment analysis"
        query_embedding = embedding_service.embed_text(query)

        results_search = service.search(
            query_embedding=query_embedding,
            top_k=3
        )

        print(f"    Query: '{query}'")
        print(f"    Résultats: {len(results_search)}")

        if results_search:
            for i, r in enumerate(results_search[:3]):
                print(f"    [{i+1}] Score: {r['score']:.4f} - Type: {r['metadata'].get('type', 'N/A')}")
            results.append(("search", True))
        else:
            print("    Aucun résultat (index peut-être vide)")
            results.append(("search", True))  # Pas une erreur si index vide

    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("search", False))

    # Test search avec filtre
    print("\n[5] Test search() avec filtre crypto")
    try:
        filter_dict = {"crypto": {"$eq": "BTC"}}
        results_filtered = service.search(
            query_embedding=query_embedding,
            top_k=3,
            filter_dict=filter_dict
        )

        print(f"    Filtre: crypto = BTC")
        print(f"    Résultats: {len(results_filtered)}")

        if results_filtered:
            all_btc = all(r['metadata'].get('crypto') == 'BTC' for r in results_filtered)
            print(f"    Tous BTC: {all_btc}")
            results.append(("search_filter", all_btc))
        else:
            print("    Aucun résultat (normal si pas de BTC indexé)")
            results.append(("search_filter", True))

    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("search_filter", False))

    # Test describe_index
    print("\n[6] Test describe_index()")
    try:
        index_info = service.describe_index()
        print(f"    Index info récupéré")
        results.append(("describe_index", True))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("describe_index", False))

    # Resume
    print("\n" + "=" * 60)
    print("RESUME")
    print("=" * 60)

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")

    print(f"\nTotal: {passed}/{total} tests passés")

    return passed == total


if __name__ == "__main__":
    success = test_pinecone()
    sys.exit(0 if success else 1)
