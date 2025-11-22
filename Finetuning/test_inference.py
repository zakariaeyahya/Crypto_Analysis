"""
Script de test pour vérifier que l'inférence utilise le modèle du dossier output
"""
import sys
from pathlib import Path
import logging

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_inference_with_output_model():
    """Tester l'inférence avec le modèle du dossier output"""
    
    logger.info("=" * 70)
    logger.info("TEST D'INFERENCE AVEC LE MODELE DU DOSSIER OUTPUT")
    logger.info("=" * 70)
    
    # Chemin vers le modèle dans output
    model_path = Path("output/models/best_model")
    
    # Vérifier que le modèle existe
    logger.info("1. Verification de l'existence du modele...")
    logger.info(f"   Chemin: {model_path.absolute()}")
    
    if not model_path.exists():
        logger.error(f"   ERREUR: Le dossier {model_path} n'existe pas!")
        return False
    
    # Vérifier les fichiers nécessaires
    required_files = ["config.json", "model.safetensors", "tokenizer_config.json"]
    logger.info("2. Verification des fichiers du modele...")
    all_files_exist = True
    for file in required_files:
        file_path = model_path / file
        exists = file_path.exists()
        status = "OK" if exists else "MANQUANT"
        logger.info(f"   {status} {file}: {'Existe' if exists else 'MANQUANT'}")
        if not exists:
            all_files_exist = False
    
    if not all_files_exist:
        logger.error("   ERREUR: Certains fichiers sont manquants!")
        return False
    
    # Vérifier le label mapping (il est dans le dossier parent models/)
    label_mapping_path = model_path.parent / "label_mapping.json"
    logger.info("3. Verification du label mapping...")
    logger.info(f"   Chemin: {label_mapping_path.absolute()}")
    if label_mapping_path.exists():
        import json
        with open(label_mapping_path, 'r') as f:
            label_mapping = json.load(f)
        logger.info(f"   Label mapping trouve: {label_mapping}")
    else:
        # Essayer aussi dans le dossier du modèle
        label_mapping_path2 = model_path / "label_mapping.json"
        if label_mapping_path2.exists():
            import json
            with open(label_mapping_path2, 'r') as f:
                label_mapping = json.load(f)
            logger.info(f"   Label mapping trouve dans le dossier du modele: {label_mapping}")
        else:
            logger.warning("   Label mapping non trouve (optionnel)")
    
    # Tester le chargement du modèle
    logger.info("4. Test de chargement du modele...")
    try:
        from transformers import RobertaForSequenceClassification, RobertaTokenizer
        
        logger.info("   Chargement du tokenizer...")
        tokenizer = RobertaTokenizer.from_pretrained(str(model_path))
        logger.info("   Tokenizer charge")
        
        logger.info("   Chargement du modele...")
        model = RobertaForSequenceClassification.from_pretrained(str(model_path))
        logger.info("   Modele charge")
        logger.info(f"   Architecture: {model.config.architectures[0]}")
        logger.info(f"   Nombre de labels: {model.config.num_labels if hasattr(model.config, 'num_labels') else 'N/A'}")
        
    except Exception as e:
        logger.error(f"   ERREUR lors du chargement: {e}")
        return False
    
    # Tester l'inférence avec le script
    logger.info("5. Test d'inference avec le script inference.py...")
    try:
        from inference import SentimentPredictor
        
        logger.info("   Initialisation du predicteur...")
        predictor = SentimentPredictor(
            model_path=str(model_path),
            use_cuda=False  # Utiliser CPU pour le test
        )
        logger.info("   Predicteur initialise")
        
        # Test avec quelques exemples
        test_tweets = [
            "Bitcoin is going to the moon!",
            "I lost all my money in crypto",
            "Bitcoin price is stable today"
        ]
        
        logger.info("6. Test de predictions...")
        for i, tweet in enumerate(test_tweets, 1):
            try:
                result = predictor.predict(tweet, return_proba=True)
                logger.info(f"   Tweet {i}: {tweet}")
                logger.info(f"   -> Sentiment: {result['label']}")
                logger.info(f"   -> Confiance: {result['confidence']:.2%}")
                logger.info(f"   -> Probabilites: {result['probabilities']}")
            except Exception as e:
                logger.error(f"   Erreur pour le tweet {i}: {e}")
                return False
        
        logger.info("TOUS LES TESTS SONT PASSES!")
        logger.info("Le modele du dossier output fonctionne correctement avec inference.py")
        return True
        
    except Exception as e:
        logger.error(f"   ERREUR lors de l'inference: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_inference_with_output_model()
    
    logger.info("=" * 70)
    if success:
        logger.info("RESULTAT: Le script inference.py utilise bien le modele du dossier output")
    else:
        logger.error("RESULTAT: Probleme detecte - voir les erreurs ci-dessus")
    logger.info("=" * 70)
    
    sys.exit(0 if success else 1)

