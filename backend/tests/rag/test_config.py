"""
Test de la configuration RAG
Vérifie que toutes les variables d'environnement sont correctement chargées.
"""

import sys
from pathlib import Path

# Ajouter backend au path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_config():
    """Test de la configuration RAG"""
    print("=" * 60)
    print("TEST CONFIGURATION RAG")
    print("=" * 60)

    from app.rag.config import (
        PINECONE_API_KEY,
        PINECONE_INDEX_NAME,
        EMBEDDING_MODEL,
        EMBEDDING_DIMENSION,
        LLM_PROVIDER,
        GROQ_API_KEY,
        GROQ_MODEL,
        RAG_TOP_K,
        RAG_MIN_SCORE,
        DATA_PATHS,
        CRYPTO_MAPPING
    )

    results = []

    # Test Pinecone
    print("\n[PINECONE]")
    if PINECONE_API_KEY:
        print(f"  PINECONE_API_KEY: {'*' * 10}...{PINECONE_API_KEY[-4:]}")
        results.append(("PINECONE_API_KEY", True))
    else:
        print("  PINECONE_API_KEY: NON DEFINI")
        results.append(("PINECONE_API_KEY", False))

    print(f"  PINECONE_INDEX_NAME: {PINECONE_INDEX_NAME}")
    results.append(("PINECONE_INDEX_NAME", bool(PINECONE_INDEX_NAME)))

    # Test Embedding
    print("\n[EMBEDDING]")
    print(f"  EMBEDDING_MODEL: {EMBEDDING_MODEL}")
    print(f"  EMBEDDING_DIMENSION: {EMBEDDING_DIMENSION}")
    results.append(("EMBEDDING_MODEL", bool(EMBEDDING_MODEL)))
    results.append(("EMBEDDING_DIMENSION", EMBEDDING_DIMENSION == 384))

    # Test LLM
    print("\n[LLM]")
    print(f"  LLM_PROVIDER: {LLM_PROVIDER}")
    results.append(("LLM_PROVIDER", LLM_PROVIDER in ["groq", "openai", "ollama"]))

    if GROQ_API_KEY:
        print(f"  GROQ_API_KEY: {'*' * 10}...{GROQ_API_KEY[-4:]}")
        results.append(("GROQ_API_KEY", True))
    else:
        print("  GROQ_API_KEY: NON DEFINI")
        results.append(("GROQ_API_KEY", False))

    print(f"  GROQ_MODEL: {GROQ_MODEL}")
    results.append(("GROQ_MODEL", bool(GROQ_MODEL)))

    # Test RAG params
    print("\n[RAG PARAMS]")
    print(f"  RAG_TOP_K: {RAG_TOP_K}")
    print(f"  RAG_MIN_SCORE: {RAG_MIN_SCORE}")
    results.append(("RAG_TOP_K", RAG_TOP_K > 0))
    results.append(("RAG_MIN_SCORE", 0 <= RAG_MIN_SCORE <= 1))

    # Test Data Paths
    print("\n[DATA PATHS]")
    for key, path in DATA_PATHS.items():
        exists = path.exists()
        status = "OK" if exists else "MANQUANT"
        print(f"  {key}: {status}")
        results.append((f"DATA_PATH_{key}", exists))

    # Test Crypto Mapping
    print("\n[CRYPTO MAPPING]")
    for name, code in CRYPTO_MAPPING.items():
        print(f"  {name} -> {code}")
    results.append(("CRYPTO_MAPPING", len(CRYPTO_MAPPING) >= 3))

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

    if passed == total:
        print("\nConfiguration OK!")
        return True
    else:
        print("\nConfiguration INCOMPLETE - Vérifiez le fichier .env")
        return False


if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)
