"""
Test de l'API Chat
Vérifie les endpoints REST du chatbot.
"""

import sys
import requests
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_api_chat():
    """Test des endpoints /api/chat/*"""
    print("=" * 60)
    print("TEST API CHAT ENDPOINTS")
    print("=" * 60)

    results = []

    # Test connexion au serveur
    print("\n[0] Vérification du serveur")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print(f"    Serveur accessible: {API_BASE_URL}")
            results.append(("server", True))
        else:
            print(f"    ERREUR: Serveur non accessible (status {response.status_code})")
            results.append(("server", False))
            print("\n    Assurez-vous que le serveur est lancé:")
            print("    uvicorn app.main:app --reload --port 8000")
            return False
    except requests.exceptions.ConnectionError:
        print(f"    ERREUR: Impossible de se connecter à {API_BASE_URL}")
        print("\n    Assurez-vous que le serveur est lancé:")
        print("    uvicorn app.main:app --reload --port 8000")
        results.append(("server", False))
        return False

    # Test GET /api/chat/health
    print("\n[1] Test GET /api/chat/health")
    try:
        response = requests.get(f"{API_BASE_URL}/api/chat/health", timeout=30)
        print(f"    Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"    Status: {data.get('status', 'unknown')}")
            print(f"    Components: {data.get('components', {})}")
            results.append(("health", True))
        else:
            print(f"    ERREUR: {response.text}")
            results.append(("health", False))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("health", False))

    # Test GET /api/chat/suggestions
    print("\n[2] Test GET /api/chat/suggestions")
    try:
        response = requests.get(f"{API_BASE_URL}/api/chat/suggestions", timeout=10)
        print(f"    Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            print(f"    Suggestions: {len(suggestions)}")
            for i, s in enumerate(suggestions[:3]):
                print(f"    [{i+1}] {s}")
            results.append(("suggestions", len(suggestions) > 0))
        else:
            print(f"    ERREUR: {response.text}")
            results.append(("suggestions", False))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("suggestions", False))

    # Test POST /api/chat/ - Question simple
    print("\n[3] Test POST /api/chat/ - Question simple")
    try:
        payload = {"message": "Quel est le sentiment de Bitcoin?"}
        response = requests.post(
            f"{API_BASE_URL}/api/chat/",
            json=payload,
            timeout=60
        )
        print(f"    Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"    Question: {data.get('question', 'N/A')}")
            print(f"    Réponse: {data.get('answer', 'N/A')[:100]}...")
            print(f"    Sources: {data.get('metadata', {}).get('num_sources', 0)}")
            print(f"    Temps: {data.get('metadata', {}).get('processing_time', 0)}s")
            results.append(("chat_simple", True))
        else:
            print(f"    ERREUR: {response.text}")
            results.append(("chat_simple", False))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("chat_simple", False))

    # Test POST /api/chat/ - Avec filtre crypto
    print("\n[4] Test POST /api/chat/ - Avec filtre crypto")
    try:
        payload = {
            "message": "Comment évolue le sentiment?",
            "crypto": "ETH"
        }
        response = requests.post(
            f"{API_BASE_URL}/api/chat/",
            json=payload,
            timeout=60
        )
        print(f"    Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"    Question: {data.get('question', 'N/A')}")
            print(f"    Réponse: {data.get('answer', 'N/A')[:100]}...")
            results.append(("chat_with_crypto", True))
        else:
            print(f"    ERREUR: {response.text}")
            results.append(("chat_with_crypto", False))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("chat_with_crypto", False))

    # Test POST /api/chat/ - Message vide (doit échouer)
    print("\n[5] Test POST /api/chat/ - Message vide (erreur attendue)")
    try:
        payload = {"message": ""}
        response = requests.post(
            f"{API_BASE_URL}/api/chat/",
            json=payload,
            timeout=10
        )
        print(f"    Status: {response.status_code}")

        if response.status_code == 400:
            print(f"    Erreur attendue: {response.json().get('detail', 'N/A')}")
            results.append(("chat_empty", True))
        else:
            print(f"    ERREUR: Devrait retourner 400, pas {response.status_code}")
            results.append(("chat_empty", False))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("chat_empty", False))

    # Test sources dans la réponse
    print("\n[6] Test vérification des sources")
    try:
        payload = {"message": "Quels sont les posts récents?"}
        response = requests.post(
            f"{API_BASE_URL}/api/chat/",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            sources = data.get('sources', [])
            print(f"    Nombre de sources: {len(sources)}")

            if sources:
                for i, src in enumerate(sources[:3]):
                    print(f"    [{i+1}] Type: {src.get('type', 'N/A')}, Crypto: {src.get('crypto', 'N/A')}, Score: {src.get('score', 0):.3f}")
                results.append(("sources", True))
            else:
                print("    Aucune source (peut-être normal si index vide)")
                results.append(("sources", True))
        else:
            results.append(("sources", False))
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
    success = test_api_chat()
    sys.exit(0 if success else 1)
