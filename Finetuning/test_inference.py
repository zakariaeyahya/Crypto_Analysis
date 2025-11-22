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
    
    print("=" * 70)
    print("TEST D'INFÉRENCE AVEC LE MODÈLE DU DOSSIER OUTPUT")
    print("=" * 70)
    
    # Chemin vers le modèle dans output
    model_path = Path("output/models/best_model")
    
    # Vérifier que le modèle existe
    print(f"\n1. Vérification de l'existence du modèle...")
    print(f"   Chemin: {model_path.absolute()}")
    
    if not model_path.exists():
        print(f"   ❌ ERREUR: Le dossier {model_path} n'existe pas!")
        return False
    
    # Vérifier les fichiers nécessaires
    required_files = ["config.json", "model.safetensors", "tokenizer_config.json"]
    print(f"\n2. Vérification des fichiers du modèle...")
    all_files_exist = True
    for file in required_files:
        file_path = model_path / file
        exists = file_path.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {file}: {'Existe' if exists else 'MANQUANT'}")
        if not exists:
            all_files_exist = False
    
    if not all_files_exist:
        print(f"   ❌ ERREUR: Certains fichiers sont manquants!")
        return False
    
    # Vérifier le label mapping (il est dans le dossier parent models/)
    label_mapping_path = model_path.parent / "label_mapping.json"
    print(f"\n3. Vérification du label mapping...")
    print(f"   Chemin: {label_mapping_path.absolute()}")
    if label_mapping_path.exists():
        import json
        with open(label_mapping_path, 'r') as f:
            label_mapping = json.load(f)
        print(f"   ✅ Label mapping trouvé: {label_mapping}")
    else:
        # Essayer aussi dans le dossier du modèle
        label_mapping_path2 = model_path / "label_mapping.json"
        if label_mapping_path2.exists():
            import json
            with open(label_mapping_path2, 'r') as f:
                label_mapping = json.load(f)
            print(f"   ✅ Label mapping trouvé dans le dossier du modèle: {label_mapping}")
        else:
            print(f"   ⚠️  Label mapping non trouvé (optionnel)")
    
    # Tester le chargement du modèle
    print(f"\n4. Test de chargement du modèle...")
    try:
        from transformers import RobertaForSequenceClassification, RobertaTokenizer
        
        print(f"   Chargement du tokenizer...")
        tokenizer = RobertaTokenizer.from_pretrained(str(model_path))
        print(f"   ✅ Tokenizer chargé")
        
        print(f"   Chargement du modèle...")
        model = RobertaForSequenceClassification.from_pretrained(str(model_path))
        print(f"   ✅ Modèle chargé")
        print(f"   Architecture: {model.config.architectures[0]}")
        print(f"   Nombre de labels: {model.config.num_labels if hasattr(model.config, 'num_labels') else 'N/A'}")
        
    except Exception as e:
        print(f"   ❌ ERREUR lors du chargement: {e}")
        return False
    
    # Tester l'inférence avec le script
    print(f"\n5. Test d'inférence avec le script inference.py...")
    try:
        from inference import SentimentPredictor
        
        print(f"   Initialisation du prédicteur...")
        predictor = SentimentPredictor(
            model_path=str(model_path),
            use_cuda=False  # Utiliser CPU pour le test
        )
        print(f"   ✅ Prédicteur initialisé")
        
        # Test avec quelques exemples
        test_tweets = [
            "Bitcoin is going to the moon! 🚀",
            "I lost all my money in crypto",
            "Bitcoin price is stable today"
        ]
        
        print(f"\n6. Test de prédictions...")
        for i, tweet in enumerate(test_tweets, 1):
            try:
                result = predictor.predict(tweet, return_proba=True)
                print(f"\n   Tweet {i}: {tweet}")
                print(f"   → Sentiment: {result['label']}")
                print(f"   → Confiance: {result['confidence']:.2%}")
                print(f"   → Probabilités: {result['probabilities']}")
            except Exception as e:
                print(f"   ❌ Erreur pour le tweet {i}: {e}")
                return False
        
        print(f"\n✅ TOUS LES TESTS SONT PASSÉS!")
        print(f"\nLe modèle du dossier output fonctionne correctement avec inference.py")
        return True
        
    except Exception as e:
        print(f"   ❌ ERREUR lors de l'inférence: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_inference_with_output_model()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ RÉSULTAT: Le script inference.py utilise bien le modèle du dossier output")
    else:
        print("❌ RÉSULTAT: Problème détecté - voir les erreurs ci-dessus")
    print("=" * 70)
    
    sys.exit(0 if success else 1)

