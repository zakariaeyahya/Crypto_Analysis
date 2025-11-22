"""
Script d'inférence pour prédire le sentiment de nouveaux tweets
"""
import torch
from pathlib import Path
from typing import List, Union
import logging
import json

from model_config import RobertaModelConfig
from preprocessing import TextPreprocessor, LabelEncoderWrapper

logger = logging.getLogger(__name__)


class SentimentPredictor:
    """Classe pour prédire le sentiment de tweets"""
    
    def __init__(self, model_path: str, tokenizer_path: str = None, 
                 config_path: str = "config.yaml", use_cuda: bool = True):
        """
        Initialiser le prédicteur
        
        Args:
            model_path: Chemin vers le modèle sauvegardé
            tokenizer_path: Chemin vers le tokenizer
            config_path: Chemin vers le fichier de configuration
            use_cuda: Utiliser CUDA si disponible
        """
        self.model_path = Path(model_path)
        self.tokenizer_path = Path(tokenizer_path) if tokenizer_path else self.model_path
        
        # Charger la configuration
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser le preprocessor
        preproc_config = self.config['preprocessing']
        self.preprocessor = TextPreprocessor(
            remove_urls=preproc_config['remove_urls'],
            handle_mentions=preproc_config['handle_mentions'],
            handle_hashtags=preproc_config['handle_hashtags'],
            normalize_spaces=preproc_config['normalize_spaces'],
            handle_emojis=preproc_config['handle_emojis']
        )
        
        # Charger le modèle
        self.model_wrapper = RobertaModelConfig(use_cuda=use_cuda)
        self.model_wrapper.load_tokenizer()
        
        # Charger le modèle
        if (self.model_path / "pytorch_model.bin").exists() or (self.model_path / "model.safetensors").exists():
            from transformers import RobertaForSequenceClassification
            self.model = RobertaForSequenceClassification.from_pretrained(str(self.model_path))
        else:
            checkpoint = torch.load(self.model_path, map_location=self.model_wrapper.device)
            self.model = self.model_wrapper.load_model()
            self.model.load_state_dict(checkpoint['model_state_dict'])
        
        self.model = self.model.to(self.model_wrapper.device)
        self.model.eval()
        
        # Charger le label encoder (si sauvegardé)
        # Chercher d'abord dans le dossier du modèle, puis dans le parent
        label_mapping_path = self.model_path / "label_mapping.json"
        if not label_mapping_path.exists():
            label_mapping_path = self.model_path.parent / "label_mapping.json"

        if label_mapping_path.exists():
            with open(label_mapping_path, 'r') as f:
                label_data = json.load(f)
                self.label_encoder = LabelEncoderWrapper()

                # Supporter les deux formats de label_mapping.json
                if 'label_mapping' in label_data and 'reverse_mapping' in label_data:
                    # Format complet
                    self.label_encoder.label_mapping = label_data['label_mapping']
                    self.label_encoder.reverse_mapping = {int(k): v for k, v in label_data['reverse_mapping'].items()}
                else:
                    # Format simple: {"Negative": 0, "Positive": 1}
                    self.label_encoder.label_mapping = label_data
                    self.label_encoder.reverse_mapping = {v: k for k, v in label_data.items()}
            logger.info(f"✅ Label mapping chargé depuis: {label_mapping_path}")
        else:
            logger.warning("⚠️  Label mapping non trouvé, utilisation des indices par défaut")
            self.label_encoder = None
        
        logger.info(f"✅ Modèle chargé depuis: {self.model_path}")
        logger.info(f"✅ Prêt pour l'inférence sur device: {self.model_wrapper.device}")
    
    def predict(self, text: str, return_proba: bool = False) -> Union[str, dict]:
        """
        Prédire le sentiment d'un texte
        
        Args:
            text: Texte à analyser
            return_proba: Si True, retourner aussi les probabilités
            
        Returns:
            Label de sentiment ou dictionnaire avec label et probabilités
        """
        # Préprocesser
        cleaned_text = self.preprocessor.clean_text(text)
        
        if not cleaned_text:
            return "NEUTRE" if not return_proba else {"label": "NEUTRE", "probabilities": {}}
        
        # Tokeniser
        encoding = self.model_wrapper.tokenizer(
            cleaned_text,
            truncation=True,
            padding='max_length',
            max_length=self.model_wrapper.max_length,
            return_tensors='pt'
        )
        
        # Déplacer sur device
        input_ids = encoding['input_ids'].to(self.model_wrapper.device)
        attention_mask = encoding['attention_mask'].to(self.model_wrapper.device)
        
        # Prédiction
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
        
        # Décoder le label
        if self.label_encoder and predicted_class in self.label_encoder.reverse_mapping:
            label = self.label_encoder.reverse_mapping[predicted_class]
        else:
            # Fallback si pas de label encoder
            label_map = {0: "NEGATIF", 1: "NEUTRE", 2: "POSITIF"}
            label = label_map.get(predicted_class, "NEUTRE")
        
        if return_proba:
            if self.label_encoder:
                proba_dict = {
                    self.label_encoder.reverse_mapping.get(i, f"Class_{i}"): float(prob)
                    for i, prob in enumerate(probabilities[0].cpu().numpy())
                }
            else:
                # Fallback si pas de label encoder
                label_map = {0: "NEGATIF", 1: "NEUTRE", 2: "POSITIF"}
                proba_dict = {
                    label_map.get(i, f"Class_{i}"): float(prob)
                    for i, prob in enumerate(probabilities[0].cpu().numpy())
                }
            return {
                "label": label,
                "probabilities": proba_dict,
                "confidence": float(probabilities[0][predicted_class].cpu().numpy())
            }
        
        return label
    
    def predict_batch(self, texts: List[str], batch_size: int = 32, 
                     return_proba: bool = False) -> List[Union[str, dict]]:
        """
        Prédire le sentiment pour plusieurs textes
        
        Args:
            texts: Liste de textes
            batch_size: Taille des batches
            return_proba: Si True, retourner aussi les probabilités
            
        Returns:
            Liste de prédictions
        """
        results = []
        
        # Préprocesser tous les textes
        cleaned_texts = [self.preprocessor.clean_text(text) for text in texts]
        
        # Traiter par batches
        for i in range(0, len(cleaned_texts), batch_size):
            batch_texts = cleaned_texts[i:i+batch_size]
            
            # Tokeniser le batch
            encoding = self.model_wrapper.tokenizer(
                batch_texts,
                truncation=True,
                padding='max_length',
                max_length=self.model_wrapper.max_length,
                return_tensors='pt'
            )
            
            # Déplacer sur device
            input_ids = encoding['input_ids'].to(self.model_wrapper.device)
            attention_mask = encoding['attention_mask'].to(self.model_wrapper.device)
            
            # Prédictions
            with torch.no_grad():
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)
                predicted_classes = torch.argmax(probabilities, dim=1).cpu().numpy()
            
            # Décoder les labels
            for j, pred_class in enumerate(predicted_classes):
                if self.label_encoder and pred_class in self.label_encoder.reverse_mapping:
                    label = self.label_encoder.reverse_mapping[pred_class]
                else:
                    label_map = {0: "NEGATIF", 1: "NEUTRE", 2: "POSITIF"}
                    label = label_map.get(int(pred_class), "NEUTRE")
                
                if return_proba:
                    if self.label_encoder:
                        proba_dict = {
                            self.label_encoder.reverse_mapping.get(k, f"Class_{k}"): float(prob)
                            for k, prob in enumerate(probabilities[j].cpu().numpy())
                        }
                    else:
                        # Fallback si pas de label encoder
                        label_map = {0: "NEGATIF", 1: "NEUTRE", 2: "POSITIF"}
                        proba_dict = {
                            label_map.get(k, f"Class_{k}"): float(prob)
                            for k, prob in enumerate(probabilities[j].cpu().numpy())
                        }
                    results.append({
                        "label": label,
                        "probabilities": proba_dict,
                        "confidence": float(probabilities[j][pred_class].cpu().numpy())
                    })
                else:
                    results.append(label)
        
        return results


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    
    logging.basicConfig(level=logging.INFO)
    
    from data_preparation import load_config
    
    # Charger la configuration
    config = load_config()
    model_path = f"{config['paths']['models_dir']}/{config['paths']['model_save_name']}"
    
    # Initialiser le prédicteur
    predictor = SentimentPredictor(
        model_path=model_path,
        config_path="config.yaml",
        use_cuda=config['training']['use_cuda']
    )
    
    # Exemples de prédictions
    test_tweets = [
        "Bitcoin is going to the moon! 🚀🚀🚀",
        "I lost all my money in crypto, this is terrible",
        "Bitcoin price is stable today",
        "Crypto market is crashing, sell everything!",
        "Just bought some BTC, feeling optimistic"
    ]
    
    print("\n" + "=" * 60)
    print("EXEMPLES DE PRÉDICTIONS")
    print("=" * 60)
    
    for tweet in test_tweets:
        result = predictor.predict(tweet, return_proba=True)
        print(f"\nTweet: {tweet}")
        print(f"Sentiment: {result['label']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Probabilités: {result['probabilities']}")

