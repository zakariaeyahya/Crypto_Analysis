"""
Test du service de retrieval
Vérifie la recherche de documents pertinents.
"""

import sys
from pathlib import Path

# Ajouter backend au path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_retriever():
    """Test du RetrieverService"""
    print("=" * 60)
    print("TEST RETRIEVER SERVICE")
    print("=" * 60)

    from app.rag.retriever_service import get_retriever_service

    results = []

    # Initialisation
    print("\n[1] Initialisation du service")
    try:
        retriever = get_retriever_service()
        print(f"    Top K: {retriever.default_top_k}")
        print(f"    Min score: {retriever.min_score}")
        results.append(("init", True))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("init", False))
        return False

    # Test extract_crypto_from_query
    print("\n[2] Test extract_crypto_from_query()")
    try:
        test_cases = [
            ("What is the sentiment of Bitcoin?", "BTC"),
            ("How is Ethereum doing?", "ETH"),
            ("Solana price prediction", "SOL"),
            ("Crypto market analysis", None),
            ("BTC is bullish", "BTC"),
            ("The ETH network", "ETH"),
        ]

        all_correct = True
        for query, expected in test_cases:
            result = retriever.extract_crypto_from_query(query)
            status = "OK" if result == expected else "FAIL"
            if result != expected:
                all_correct = False
            print(f"    '{query[:30]}...' -> {result} ({status})")

        results.append(("extract_crypto", all_correct))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("extract_crypto", False))

    # Test build_filter
    print("\n[3] Test build_filter()")
    try:
        # Sans filtre
        f1 = retriever.build_filter()
        print(f"    Pas de filtre: {f1}")

        # Filtre crypto
        f2 = retriever.build_filter(crypto="BTC")
        print(f"    Crypto BTC: {f2}")

        # Filtre type
        f3 = retriever.build_filter(doc_type="post")
        print(f"    Type post: {f3}")

        # Filtre combiné
        f4 = retriever.build_filter(crypto="ETH", doc_type="analysis")
        print(f"    ETH + analysis: {f4}")

        results.append(("build_filter", True))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("build_filter", False))

    # Test retrieve
    print("\n[4] Test retrieve()")
    try:
        query = "Quel est le sentiment de Bitcoin?"
        docs = retriever.retrieve(query, top_k=3)

        print(f"    Query: '{query}'")
        print(f"    Résultats: {len(docs)}")

        if docs:
            for i, doc in enumerate(docs[:3]):
                print(f"    [{i+1}] Score: {doc['score']:.4f}")
                print(f"        Type: {doc['metadata'].get('type', 'N/A')}")
                print(f"        Crypto: {doc['metadata'].get('crypto', 'N/A')}")
            results.append(("retrieve", True))
        else:
            print("    Aucun résultat (index peut-être vide)")
            results.append(("retrieve", True))

    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("retrieve", False))

    # Test retrieve_with_context
    print("\n[5] Test retrieve_with_context()")
    try:
        query = "Comment évolue Ethereum?"
        result = retriever.retrieve_with_context(query, top_k=3)

        print(f"    Query: '{query}'")
        print(f"    Num results: {result['num_results']}")
        print(f"    Context length: {len(result['context'])} chars")

        if result['context']:
            print(f"    Context preview: {result['context'][:100]}...")

        results.append(("retrieve_with_context", True))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("retrieve_with_context", False))

    # Test retrieve_by_types
    print("\n[6] Test retrieve_by_types()")
    try:
        query = "Analyse du marché crypto"
        doc_types = ["post", "analysis", "daily_summary"]
        docs = retriever.retrieve_by_types(query, doc_types, top_k_per_type=2)

        print(f"    Query: '{query}'")
        print(f"    Types recherchés: {doc_types}")
        print(f"    Résultats: {len(docs)}")

        if docs:
            types_found = set(d['metadata'].get('type', 'N/A') for d in docs)
            print(f"    Types trouvés: {types_found}")

        results.append(("retrieve_by_types", True))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("retrieve_by_types", False))

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
    success = test_retriever()
    sys.exit(0 if success else 1)
