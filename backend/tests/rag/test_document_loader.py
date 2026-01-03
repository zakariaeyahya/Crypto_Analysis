"""
Test du chargement des documents
Vérifie que tous les documents sont correctement chargés depuis les fichiers JSON/CSV.
"""

import sys
from pathlib import Path

# Ajouter backend au path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_document_loader():
    """Test du DocumentLoader"""
    print("=" * 60)
    print("TEST DOCUMENT LOADER")
    print("=" * 60)

    from app.rag.document_loader import DocumentLoader

    loader = DocumentLoader()
    results = []

    # Test load_posts
    print("\n[1] Test load_posts()")
    try:
        posts = loader.load_posts()
        print(f"    Documents chargés: {len(posts)}")
        if posts:
            print(f"    Premier post: {posts[0].get('id', 'N/A')}")
            print(f"    Crypto: {posts[0].get('crypto', 'N/A')}")
            print(f"    Texte: {posts[0].get('text', '')[:50]}...")
        results.append(("load_posts", len(posts) > 0))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("load_posts", False))

    # Test load_timeseries
    print("\n[2] Test load_timeseries()")
    try:
        timeseries = loader.load_timeseries()
        print(f"    Documents chargés: {len(timeseries)}")
        if timeseries:
            print(f"    Premier: {timeseries[0].get('id', 'N/A')}")
        results.append(("load_timeseries", len(timeseries) > 0))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("load_timeseries", False))

    # Test load_correlations
    print("\n[3] Test load_correlations()")
    try:
        correlations = loader.load_correlations()
        print(f"    Documents chargés: {len(correlations)}")
        if correlations:
            print(f"    Premier: {correlations[0].get('id', 'N/A')}")
        results.append(("load_correlations", len(correlations) > 0))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("load_correlations", False))

    # Test load_lag_analysis
    print("\n[4] Test load_lag_analysis()")
    try:
        lag = loader.load_lag_analysis()
        print(f"    Documents chargés: {len(lag)}")
        if lag:
            print(f"    Premier: {lag[0].get('id', 'N/A')}")
        results.append(("load_lag_analysis", len(lag) > 0))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("load_lag_analysis", False))

    # Test load_prices
    print("\n[5] Test load_prices()")
    try:
        prices = loader.load_prices()
        print(f"    Documents chargés: {len(prices)}")
        if prices:
            print(f"    Premier: {prices[0].get('id', 'N/A')}")
        results.append(("load_prices", len(prices) > 0))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("load_prices", False))

    # Test load_faq
    print("\n[6] Test load_faq()")
    try:
        faq = loader.load_faq()
        print(f"    Documents chargés: {len(faq)}")
        if faq:
            print(f"    Premier: {faq[0].get('text', '')[:50]}...")
        results.append(("load_faq", len(faq) > 0))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("load_faq", False))

    # Test load_all
    print("\n[7] Test load_all()")
    try:
        all_docs = loader.load_all()
        print(f"    Total documents: {len(all_docs)}")
        stats = loader.get_stats()
        print(f"    Stats: {stats}")
        results.append(("load_all", len(all_docs) > 0))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("load_all", False))

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
    success = test_document_loader()
    sys.exit(0 if success else 1)
