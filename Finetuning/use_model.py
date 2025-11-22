"""
Script simple pour utiliser le modèle entraîné du dossier output/models
"""
import sys
from pathlib import Path
import logging

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).resolve().parent))

from inference import SentimentPredictor

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Chemin vers le modèle dans output/models
    model_path = "output/models/best_model"  # ou "output/models/final_model"

    logger.info("Chargement du modele...")
    predictor = SentimentPredictor(
        model_path=model_path,
        config_path="config.yaml",
        use_cuda=False  # Mettez True si vous avez un GPU
    )
    logger.info("Modele charge!")

    # Exemples de tweets à analyser
    tweets = [
        "Bitcoin is going to the moon!",
        "I lost all my money in crypto",
        "Bitcoin price is stable today",
        "This is the best investment ever!",
        "Crypto market is crashing hard"
    ]

    logger.info("=" * 60)
    logger.info("PREDICTIONS DE SENTIMENT")
    logger.info("=" * 60)

    for tweet in tweets:
        result = predictor.predict(tweet, return_proba=True)
        logger.info(f"Tweet: {tweet}")
        logger.info(f"   Sentiment: {result['label']}")
        logger.info(f"   Confiance: {result['confidence']:.2%}")
        logger.info(f"   Probabilites: {result['probabilities']}")

    # Prédiction interactive
    logger.info("=" * 60)
    logger.info("MODE INTERACTIF (tapez 'quit' pour quitter)")
    logger.info("=" * 60)

    while True:
        user_text = input("\nEntrez un tweet: ")
        if user_text.lower() in ['quit', 'exit', 'q']:
            break

        result = predictor.predict(user_text, return_proba=True)
        logger.info(f"   -> Sentiment: {result['label']}")
        logger.info(f"   -> Confiance: {result['confidence']:.2%}")
        logger.info(f"   -> Probabilites: {result['probabilities']}")

    logger.info("Au revoir!")

if __name__ == "__main__":
    main()
