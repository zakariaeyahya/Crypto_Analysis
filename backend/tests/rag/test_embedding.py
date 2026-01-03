"""
Test du service d'embedding
Vérifie que le modèle génère correctement les vecteurs.
"""

import sys
from pathlib import Path

# Ajouter backend au path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_embedding():
    """Test du EmbeddingService"""
    print("=" * 60)
    print("TEST EMBEDDING SERVICE")
    print("=" * 60)

    from app.rag.embedding_service import get_embedding_service

    results = []

    # Initialisation
    print("\n[1] Initialisation du service")
    try:
        service = get_embedding_service()
        info = service.get_model_info()
        print(f"    Modèle: {info['model_name']}")
        print(f"    Dimension: {info['dimension']}")
        print(f"    Batch size: {info['batch_size']}")
        results.append(("init", True))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("init", False))
        return False

    # Test embed_text
    print("\n[2] Test embed_text() - texte simple")
    try:
        text = "Bitcoin is a decentralized cryptocurrency"
        embedding = service.embed_text(text)
        print(f"    Input: '{text}'")
        print(f"    Output: vecteur de dimension {len(embedding)}")
        print(f"    Premiers éléments: {embedding[:5]}")
        ok = len(embedding) == 384
        results.append(("embed_text", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("embed_text", False))

    # Test embed_text en français
    print("\n[3] Test embed_text() - texte français")
    try:
        text_fr = "Le sentiment de Bitcoin est positif aujourd'hui"
        embedding_fr = service.embed_text(text_fr)
        print(f"    Input: '{text_fr}'")
        print(f"    Output: vecteur de dimension {len(embedding_fr)}")
        ok = len(embedding_fr) == 384
        results.append(("embed_text_fr", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("embed_text_fr", False))

    # Test embed_texts_batch
    print("\n[4] Test embed_texts_batch() - plusieurs textes")
    try:
        texts = [
            "Bitcoin price is going up",
            "Ethereum smart contracts",
            "Solana fast transactions",
            "Crypto market analysis"
        ]
        embeddings = service.embed_texts_batch(texts)
        print(f"    Input: {len(texts)} textes")
        print(f"    Output: {len(embeddings)} vecteurs")
        print(f"    Dimension de chaque: {len(embeddings[0])}")
        ok = len(embeddings) == len(texts) and all(len(e) == 384 for e in embeddings)
        results.append(("embed_batch", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("embed_batch", False))

    # Test embed_chunks
    print("\n[5] Test embed_chunks() - chunks avec métadonnées")
    try:
        chunks = [
            {"id": "chunk_1", "text": "Bitcoin sentiment analysis"},
            {"id": "chunk_2", "text": "Ethereum price prediction"},
            {"id": "chunk_3", "text": "Crypto market trends"},
        ]
        chunks_with_emb = service.embed_chunks(chunks, show_progress=False)
        print(f"    Input: {len(chunks)} chunks")
        print(f"    Output: {len(chunks_with_emb)} chunks avec embeddings")

        # Vérifier que chaque chunk a un embedding
        all_have_emb = all("embedding" in c for c in chunks_with_emb)
        all_correct_dim = all(len(c["embedding"]) == 384 for c in chunks_with_emb)
        print(f"    Tous ont embedding: {all_have_emb}")
        print(f"    Dimension correcte: {all_correct_dim}")

        ok = all_have_emb and all_correct_dim
        results.append(("embed_chunks", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("embed_chunks", False))

    # Test similarité sémantique
    print("\n[6] Test similarité sémantique")
    try:
        import numpy as np

        text1 = "Bitcoin price is increasing"
        text2 = "BTC value is going up"
        text3 = "The weather is sunny today"

        emb1 = np.array(service.embed_text(text1))
        emb2 = np.array(service.embed_text(text2))
        emb3 = np.array(service.embed_text(text3))

        # Similarité cosinus
        sim_12 = np.dot(emb1, emb2)
        sim_13 = np.dot(emb1, emb3)

        print(f"    '{text1}' vs '{text2}': {sim_12:.4f}")
        print(f"    '{text1}' vs '{text3}': {sim_13:.4f}")

        # Les textes similaires devraient avoir un score plus élevé
        ok = sim_12 > sim_13
        print(f"    Similarité sémantique correcte: {ok}")
        results.append(("semantic_similarity", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("semantic_similarity", False))

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
    success = test_embedding()
    sys.exit(0 if success else 1)
