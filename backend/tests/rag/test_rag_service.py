"""
Test du service RAG complet
Vérifie le pipeline RAG de bout en bout.
"""

import sys
from pathlib import Path

# Ajouter backend au path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_rag_service():
    """Test du RAGService"""
    print("=" * 60)
    print("TEST RAG SERVICE (Pipeline complet)")
    print("=" * 60)

    from app.rag.rag_service import get_rag_service

    results = []

    # Initialisation
    print("\n[1] Initialisation du service RAG")
    try:
        rag = get_rag_service()
        config = rag.get_config()
        print(f"    Top K: {config['top_k']}")
        print(f"    Include sources: {config['include_sources']}")
        results.append(("init", True))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("init", False))
        return False

    # Test health_check
    print("\n[2] Test health_check()")
    try:
        health = rag.health_check()
        print(f"    Overall: {health.get('overall', 'unknown')}")
        print(f"    RAG Service: {health.get('rag_service', 'unknown')}")
        print(f"    Retriever: {health.get('retriever', 'unknown')}")
        print(f"    LLM: {health.get('llm', 'unknown')}")
        print(f"    Pinecone: {health.get('pinecone', 'unknown')}")

        ok = health.get('overall') in ['ok', 'degraded']
        results.append(("health_check", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("health_check", False))

    # Test process_query - Bitcoin
    print("\n[3] Test process_query() - Question Bitcoin")
    try:
        question = "Quel est le sentiment actuel de Bitcoin?"
        result = rag.process_query(question)

        print(f"    Question: '{question}'")
        print(f"    Réponse: {result['answer'][:150]}...")
        print(f"    Sources: {result['metadata']['num_sources']}")
        print(f"    Temps: {result['metadata']['processing_time']}s")
        print(f"    Modèle: {result['metadata']['model_used']}")

        ok = len(result['answer']) > 10
        results.append(("process_query_btc", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("process_query_btc", False))

    # Test process_query - Ethereum
    print("\n[4] Test process_query() - Question Ethereum")
    try:
        question = "Comment évolue le sentiment Ethereum cette semaine?"
        result = rag.process_query(question)

        print(f"    Question: '{question}'")
        print(f"    Réponse: {result['answer'][:150]}...")
        print(f"    Sources: {result['metadata']['num_sources']}")

        ok = len(result['answer']) > 10
        results.append(("process_query_eth", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("process_query_eth", False))

    # Test process_query - Question générale
    print("\n[5] Test process_query() - Question générale")
    try:
        question = "Y a-t-il une corrélation entre sentiment et prix?"
        result = rag.process_query(question)

        print(f"    Question: '{question}'")
        print(f"    Réponse: {result['answer'][:150]}...")
        print(f"    Sources: {result['metadata']['num_sources']}")

        ok = len(result['answer']) > 10
        results.append(("process_query_general", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("process_query_general", False))

    # Test get_quick_answer
    print("\n[6] Test get_quick_answer()")
    try:
        question = "Solana est-il bullish ou bearish?"
        answer = rag.get_quick_answer(question)

        print(f"    Question: '{question}'")
        print(f"    Réponse: {answer[:150]}...")

        ok = len(answer) > 10
        results.append(("quick_answer", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("quick_answer", False))

    # Test get_crypto_summary
    print("\n[7] Test get_crypto_summary()")
    try:
        result = rag.get_crypto_summary("BTC")

        print(f"    Crypto: BTC")
        print(f"    Résumé: {result['answer'][:150]}...")
        print(f"    Sources: {result['metadata']['num_sources']}")

        ok = len(result['answer']) > 10
        results.append(("crypto_summary", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("crypto_summary", False))

    # Test compare_cryptos
    print("\n[8] Test compare_cryptos()")
    try:
        result = rag.compare_cryptos(["BTC", "ETH"])

        print(f"    Cryptos: BTC, ETH")
        print(f"    Comparaison: {result['answer'][:150]}...")
        print(f"    Sources: {result['metadata']['num_sources']}")

        ok = len(result['answer']) > 10
        results.append(("compare_cryptos", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("compare_cryptos", False))

    # Test sources dans la réponse
    print("\n[9] Test présence des sources")
    try:
        question = "Quels sont les posts récents sur Bitcoin?"
        result = rag.process_query(question)

        sources = result.get('sources', [])
        print(f"    Question: '{question}'")
        print(f"    Nombre de sources: {len(sources)}")

        if sources:
            for i, src in enumerate(sources[:3]):
                print(f"    [{i+1}] {src.get('type', 'N/A')} - {src.get('crypto', 'N/A')} - Score: {src.get('score', 0):.3f}")

        ok = len(sources) > 0
        results.append(("sources", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("sources", False))

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
    success = test_rag_service()
    sys.exit(0 if success else 1)
