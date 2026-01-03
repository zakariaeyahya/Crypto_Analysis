"""
Test du service LLM
Vérifie la connexion et la génération de texte avec Groq/OpenAI/Ollama.
"""

import sys
from pathlib import Path

# Ajouter backend au path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_llm():
    """Test du LLMService"""
    print("=" * 60)
    print("TEST LLM SERVICE")
    print("=" * 60)

    from app.rag.config import LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL

    results = []

    # Vérifier la configuration
    print("\n[1] Vérification de la configuration")
    print(f"    Provider: {LLM_PROVIDER}")
    print(f"    Modèle: {GROQ_MODEL}")

    if LLM_PROVIDER == "groq" and not GROQ_API_KEY:
        print("    ERREUR: GROQ_API_KEY non défini dans .env")
        results.append(("config", False))
    else:
        if GROQ_API_KEY:
            print(f"    Clé API: {'*' * 10}...{GROQ_API_KEY[-4:]}")
        results.append(("config", True))

    # Initialisation du service
    print("\n[2] Initialisation du service LLM")
    try:
        from app.rag.llm_service import get_llm_service

        llm = get_llm_service()
        info = llm.get_provider_info()
        print(f"    Provider: {info['provider']}")
        print(f"    Available: {info['available']}")
        results.append(("init", info['available']))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("init", False))
        return False

    # Test is_available
    print("\n[3] Test is_available()")
    try:
        available = llm.is_available()
        print(f"    LLM disponible: {available}")
        results.append(("is_available", available))

        if not available:
            print("    Le LLM n'est pas disponible. Les tests suivants seront ignorés.")
            return False
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("is_available", False))
        return False

    # Test generate simple
    print("\n[4] Test generate() - prompt simple")
    try:
        prompt = "Réponds en une phrase: Qu'est-ce que Bitcoin?"
        response = llm.generate(prompt)

        print(f"    Prompt: '{prompt}'")
        print(f"    Réponse: {response[:200]}...")
        print(f"    Longueur: {len(response)} caractères")

        ok = len(response) > 10
        results.append(("generate_simple", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("generate_simple", False))

    # Test generate avec system prompt
    print("\n[5] Test generate() - avec system prompt")
    try:
        system_prompt = "Tu es un expert en cryptomonnaies. Réponds de manière concise."
        user_prompt = "Quel est le sentiment actuel du marché Bitcoin?"

        response = llm.generate(user_prompt, system_prompt=system_prompt)

        print(f"    System: '{system_prompt[:50]}...'")
        print(f"    User: '{user_prompt}'")
        print(f"    Réponse: {response[:200]}...")

        ok = len(response) > 10
        results.append(("generate_system", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("generate_system", False))

    # Test generate_with_context
    print("\n[6] Test generate_with_context()")
    try:
        context = """
        [Document 1] (Type: post)
        Crypto: BTC
        Contenu: Bitcoin is showing strong bullish momentum today.

        [Document 2] (Type: daily_summary)
        Crypto: BTC
        Contenu: Résumé BTC du 2024-01-15: Sentiment moyen 0.65. 45 positifs, 12 négatifs.
        """
        question = "Quel est le sentiment de Bitcoin?"

        response = llm.generate_with_context(question, context)

        print(f"    Question: '{question}'")
        print(f"    Context: {len(context)} caractères")
        print(f"    Réponse: {response[:200]}...")

        ok = len(response) > 10
        results.append(("generate_with_context", ok))
    except Exception as e:
        print(f"    ERREUR: {e}")
        results.append(("generate_with_context", False))

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
    success = test_llm()
    sys.exit(0 if success else 1)
