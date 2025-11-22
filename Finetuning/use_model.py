"""
Script simple pour utiliser le modèle entraîné du dossier output/models
"""
import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).resolve().parent))

from inference import SentimentPredictor

def main():
    # Chemin vers le modèle dans output/models
    model_path = "output/models/best_model"  # ou "output/models/final_model"

    print("🔄 Chargement du modèle...")
    predictor = SentimentPredictor(
        model_path=model_path,
        config_path="config.yaml",
        use_cuda=False  # Mettez True si vous avez un GPU
    )
    print("✅ Modèle chargé !\n")

    # Exemples de tweets à analyser
    tweets = [
        "Bitcoin is going to the moon! 🚀",
        "I lost all my money in crypto",
        "Bitcoin price is stable today",
        "This is the best investment ever!",
        "Crypto market is crashing hard"
    ]

    print("=" * 60)
    print("PRÉDICTIONS DE SENTIMENT")
    print("=" * 60)

    for tweet in tweets:
        result = predictor.predict(tweet, return_proba=True)
        print(f"\n📝 Tweet: {tweet}")
        print(f"   Sentiment: {result['label']}")
        print(f"   Confiance: {result['confidence']:.2%}")
        print(f"   Probabilités: {result['probabilities']}")

    # Prédiction interactive
    print("\n" + "=" * 60)
    print("MODE INTERACTIF (tapez 'quit' pour quitter)")
    print("=" * 60)

    while True:
        user_text = input("\n📝 Entrez un tweet: ")
        if user_text.lower() in ['quit', 'exit', 'q']:
            break

        result = predictor.predict(user_text, return_proba=True)
        print(f"   → Sentiment: {result['label']}")
        print(f"   → Confiance: {result['confidence']:.2%}")
        print(f"   → Probabilités: {result['probabilities']}")

    print("\n👋 Au revoir!")

if __name__ == "__main__":
    main()
