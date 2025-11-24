"""
Simple script to use the trained model from output/models directory
"""
import sys
from pathlib import Path
import logging

# Add project path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from inference import SentimentPredictor

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Path to model in output/models
    model_path = "output/models/best_model"  # or "output/models/final_model"

    logger.info("Loading model...")
    predictor = SentimentPredictor(
        model_path=model_path,
        config_path="config.yaml",
        use_cuda=False  # Set to True if you have a GPU
    )
    logger.info("Model loaded!")

    # Example tweets to analyze
    tweets = [
        "Bitcoin is going to the moon!",
        "I lost all my money in crypto",
        "Bitcoin price is stable today",
        "This is the best investment ever!",
        "Crypto market is crashing hard"
    ]

    logger.info("=" * 60)
    logger.info("SENTIMENT PREDICTIONS")
    logger.info("=" * 60)

    for tweet in tweets:
        result = predictor.predict(tweet, return_proba=True)
        logger.info(f"Tweet: {tweet}")
        logger.info(f"   Sentiment: {result['label']}")
        logger.info(f"   Confidence: {result['confidence']:.2%}")
        logger.info(f"   Probabilities: {result['probabilities']}")

    # Interactive prediction
    logger.info("=" * 60)
    logger.info("INTERACTIVE MODE (type 'quit' to exit)")
    logger.info("=" * 60)

    while True:
        user_text = input("\nEnter a tweet: ")
        if user_text.lower() in ['quit', 'exit', 'q']:
            break

        result = predictor.predict(user_text, return_proba=True)
        logger.info(f"   -> Sentiment: {result['label']}")
        logger.info(f"   -> Confidence: {result['confidence']:.2%}")
        logger.info(f"   -> Probabilities: {result['probabilities']}")

    logger.info("Goodbye!")

if __name__ == "__main__":
    main()
