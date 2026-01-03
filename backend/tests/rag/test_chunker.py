"""
Test du découpage en chunks
Vérifie que les documents sont correctement découpés en morceaux.
"""

import sys
from pathlib import Path

# Ajouter backend au path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_chunker():
    """Test du DocumentChunker"""
    print("=" * 60)
    print("TEST CHUNKER")
    print("=" * 60)

    from app.rag.chunker import DocumentChunker

    chunker = DocumentChunker(chunk_size=500, overlap=50)
    results = []

    # Test 1: Document court (pas de découpage)
    print("\n[1] Test document court (< 500 chars)")
    short_doc = {
        "id": "test_short",
        "type": "test",
        "crypto": "BTC",
        "text": "Bitcoin est une crypto-monnaie décentralisée."
    }

    try:
        chunks = chunker.chunk_document(short_doc)
        print(f"    Input: {len(short_doc['text'])} chars")
        print(f"    Output: {len(chunks)} chunk(s)")
        print(f"    ID: {chunks[0]['id']}")
        ok = len(chunks) == 1
        results.append(("short_document", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("short_document", False))

    # Test 2: Document long (découpage)
    print("\n[2] Test document long (> 500 chars)")
    long_text = """
    Bitcoin est la première crypto-monnaie décentralisée créée en 2009 par Satoshi Nakamoto.
    Elle utilise la technologie blockchain pour sécuriser les transactions.
    Le réseau Bitcoin permet d'envoyer et de recevoir des paiements sans intermédiaire.
    La limite de 21 millions de bitcoins crée une rareté numérique.
    Le halving réduit de moitié la récompense des mineurs tous les 4 ans.
    Bitcoin est considéré comme de l'or numérique par beaucoup d'investisseurs.
    La volatilité du marché crypto reste élevée mais la tendance long terme est haussière.
    De nombreuses entreprises acceptent maintenant Bitcoin comme moyen de paiement.
    Les institutions financières commencent à investir massivement dans Bitcoin.
    L'adoption mondiale de Bitcoin continue de croître année après année.
    """

    long_doc = {
        "id": "test_long",
        "type": "test",
        "crypto": "BTC",
        "text": long_text.strip()
    }

    try:
        chunks = chunker.chunk_document(long_doc)
        print(f"    Input: {len(long_doc['text'])} chars")
        print(f"    Output: {len(chunks)} chunk(s)")
        for i, chunk in enumerate(chunks):
            print(f"    Chunk {i}: {len(chunk['text'])} chars - {chunk['id']}")
        ok = len(chunks) > 1
        results.append(("long_document", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("long_document", False))

    # Test 3: Chunk_all avec plusieurs documents
    print("\n[3] Test chunk_all() avec plusieurs documents")
    docs = [short_doc, long_doc]

    try:
        all_chunks = chunker.chunk_all(docs)
        print(f"    Input: {len(docs)} documents")
        print(f"    Output: {len(all_chunks)} chunks")
        ok = len(all_chunks) >= len(docs)
        results.append(("chunk_all", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("chunk_all", False))

    # Test 4: Statistiques
    print("\n[4] Test get_stats()")
    try:
        stats = chunker.get_stats(all_chunks)
        print(f"    Total chunks: {stats['total_chunks']}")
        print(f"    Avg length: {stats['avg_length']}")
        print(f"    Min length: {stats['min_length']}")
        print(f"    Max length: {stats['max_length']}")
        print(f"    By type: {stats['by_type']}")
        ok = stats['total_chunks'] > 0
        results.append(("get_stats", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("get_stats", False))

    # Test 5: Vérifier que les chunks ne dépassent pas la taille max
    print("\n[5] Test taille maximale des chunks")
    try:
        all_valid = all(len(c['text']) <= 600 for c in all_chunks)  # 500 + marge overlap
        print(f"    Tous les chunks <= 600 chars: {all_valid}")
        results.append(("max_size", all_valid))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("max_size", False))

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
    success = test_chunker()
    sys.exit(0 if success else 1)
