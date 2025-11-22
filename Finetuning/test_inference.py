"""
Test script to verify that inference uses the model from the output directory
"""
import sys
from pathlib import Path
import logging

# Add project path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_inference_with_output_model():
    """Test inference with model from output directory"""
    
    logger.info("=" * 70)
    logger.info("TEST INFERENCE WITH MODEL FROM OUTPUT DIRECTORY")
    logger.info("=" * 70)
    
    # Path to model in output
    model_path = Path("output/models/best_model")
    
    # Check that model exists
    logger.info("1. Checking model existence...")
    logger.info(f"   Path: {model_path.absolute()}")
    
    if not model_path.exists():
        logger.error(f"   ERROR: Directory {model_path} does not exist!")
        return False
    
    # Check required files
    required_files = ["config.json", "model.safetensors", "tokenizer_config.json"]
    logger.info("2. Checking model files...")
    all_files_exist = True
    for file in required_files:
        file_path = model_path / file
        exists = file_path.exists()
        status = "OK" if exists else "MISSING"
        logger.info(f"   {status} {file}: {'Exists' if exists else 'MISSING'}")
        if not exists:
            all_files_exist = False
    
    if not all_files_exist:
        logger.error("   ERROR: Some files are missing!")
        return False
    
    # Check label mapping (it's in the parent models/ directory)
    label_mapping_path = model_path.parent / "label_mapping.json"
    logger.info("3. Checking label mapping...")
    logger.info(f"   Path: {label_mapping_path.absolute()}")
    if label_mapping_path.exists():
        import json
        with open(label_mapping_path, 'r') as f:
            label_mapping = json.load(f)
        logger.info(f"   Label mapping found: {label_mapping}")
    else:
        # Try also in model directory
        label_mapping_path2 = model_path / "label_mapping.json"
        if label_mapping_path2.exists():
            import json
            with open(label_mapping_path2, 'r') as f:
                label_mapping = json.load(f)
            logger.info(f"   Label mapping found in model directory: {label_mapping}")
        else:
            logger.warning("   Label mapping not found (optional)")
    
    # Test model loading
    logger.info("4. Testing model loading...")
    try:
        from transformers import RobertaForSequenceClassification, RobertaTokenizer
        
        logger.info("   Loading tokenizer...")
        tokenizer = RobertaTokenizer.from_pretrained(str(model_path))
        logger.info("   Tokenizer loaded")
        
        logger.info("   Loading model...")
        model = RobertaForSequenceClassification.from_pretrained(str(model_path))
        logger.info("   Model loaded")
        logger.info(f"   Architecture: {model.config.architectures[0]}")
        logger.info(f"   Number of labels: {model.config.num_labels if hasattr(model.config, 'num_labels') else 'N/A'}")
        
    except Exception as e:
        logger.error(f"   ERROR during loading: {e}")
        return False
    
    # Test inference with script
    logger.info("5. Testing inference with inference.py script...")
    try:
        from inference import SentimentPredictor
        
        logger.info("   Initializing predictor...")
        predictor = SentimentPredictor(
            model_path=str(model_path),
            use_cuda=False  # Use CPU for test
        )
        logger.info("   Predictor initialized")
        
        # Test with some examples
        test_tweets = [
            "Bitcoin is going to the moon!",
            "I lost all my money in crypto",
            "Bitcoin price is stable today"
        ]
        
        logger.info("6. Testing predictions...")
        for i, tweet in enumerate(test_tweets, 1):
            try:
                result = predictor.predict(tweet, return_proba=True)
                logger.info(f"   Tweet {i}: {tweet}")
                logger.info(f"   -> Sentiment: {result['label']}")
                logger.info(f"   -> Confidence: {result['confidence']:.2%}")
                logger.info(f"   -> Probabilities: {result['probabilities']}")
            except Exception as e:
                logger.error(f"   Error for tweet {i}: {e}")
                return False
        
        logger.info("ALL TESTS PASSED!")
        logger.info("Model from output directory works correctly with inference.py")
        return True
        
    except Exception as e:
        logger.error(f"   ERROR during inference: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_inference_with_output_model()
    
    logger.info("=" * 70)
    if success:
        logger.info("RESULT: inference.py script correctly uses model from output directory")
    else:
        logger.error("RESULT: Problem detected - see errors above")
    logger.info("=" * 70)
    
    sys.exit(0 if success else 1)

