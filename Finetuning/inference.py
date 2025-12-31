"""
Sentiment Analysis Inference Module
Provides SentimentPredictor class for making predictions with the trained model
"""
import torch
from transformers import RobertaForSequenceClassification, RobertaTokenizer
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SentimentPredictor:
    """Sentiment prediction class using trained RoBERTa model"""

    def __init__(self, model_path=None, use_cuda=True):
        """
        Initialize the predictor

        Args:
            model_path: Path to the trained model (default: output/models/best_model)
            use_cuda: Whether to use CUDA if available
        """
        if model_path is None:
            model_path = Path("output/models/best_model")
        else:
            model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")

        # Setup device
        self.device = torch.device("cuda" if use_cuda and torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

        # Load tokenizer and model
        logger.info(f"Loading model from {model_path}")
        self.tokenizer = RobertaTokenizer.from_pretrained(str(model_path))
        self.model = RobertaForSequenceClassification.from_pretrained(str(model_path))
        self.model.to(self.device)
        self.model.eval()

        # Label mapping (2 labels: Positive=0, Negative=1)
        # NOTE: Based on inference results, the model was trained with this mapping
        self.label_map = {0: "positive", 1: "negative"}
        self.num_labels = self.model.config.num_labels

        logger.info(f"Model loaded successfully with {self.num_labels} labels")

    def predict(self, text, return_proba=False):
        """
        Predict sentiment for a single text

        Args:
            text: Input text to analyze
            return_proba: If True, return probabilities for all labels

        Returns:
            dict with keys:
                - label: predicted sentiment label
                - confidence: confidence score for the prediction
                - probabilities: dict of all label probabilities (if return_proba=True)
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)

        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            prediction = torch.argmax(probs, dim=-1).item()
            confidence = torch.max(probs, dim=-1).values.item()

        result = {
            "label": self.label_map[prediction],
            "confidence": confidence
        }

        if return_proba:
            probabilities = {
                self.label_map[i]: probs[0][i].item()
                for i in range(self.num_labels)
            }
            result["probabilities"] = probabilities

        return result

    def predict_batch(self, texts, batch_size=32):
        """
        Predict sentiment for multiple texts

        Args:
            texts: List of texts to analyze
            batch_size: Batch size for processing

        Returns:
            List of dicts with predictions for each text
        """
        results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Tokenize batch
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)

            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
                predictions = torch.argmax(probs, dim=-1)
                confidences = torch.max(probs, dim=-1).values

            # Convert to results
            for pred, conf in zip(predictions.cpu().numpy(), confidences.cpu().numpy()):
                results.append({
                    "label": self.label_map[pred],
                    "confidence": float(conf)
                })

        return results


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    predictor = SentimentPredictor(use_cuda=False)

    test_texts = [
        "Bitcoin is going to the moon!",
        "I lost all my money in crypto",
        "Bitcoin price is stable today"
    ]

    print("\n" + "="*60)
    print("SENTIMENT ANALYSIS EXAMPLES")
    print("="*60)

    for text in test_texts:
        result = predictor.predict(text, return_proba=True)
        print(f"\nText: {text}")
        print(f"Sentiment: {result['label']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Probabilities: {result['probabilities']}")
