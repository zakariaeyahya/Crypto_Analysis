"""
Évaluation du modèle fine-tuné
"""
import torch
import pandas as pd
import numpy as np
from pathlib import Path
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    classification_report, confusion_matrix
)
import json
import logging
from typing import Dict, Any

from model_config import RobertaModelConfig
from train import TweetDataset
from preprocessing import LabelEncoderWrapper

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Classe pour évaluer le modèle fine-tuné"""
    
    def __init__(self, model_path: str, tokenizer_path: str = None, use_cuda: bool = True):
        """
        Initialiser l'évaluateur
        
        Args:
            model_path: Chemin vers le modèle sauvegardé
            tokenizer_path: Chemin vers le tokenizer (si différent du modèle)
            use_cuda: Utiliser CUDA si disponible
        """
        self.model_path = Path(model_path)
        self.tokenizer_path = Path(tokenizer_path) if tokenizer_path else self.model_path
        
        # Charger le modèle
        self.model_wrapper = RobertaModelConfig(use_cuda=use_cuda)
        self.model_wrapper.load_tokenizer()
        
        # Charger le modèle depuis le checkpoint ou directement
        if (self.model_path / "pytorch_model.bin").exists() or (self.model_path / "model.safetensors").exists():
            # Modèle sauvegardé avec save_pretrained
            from transformers import RobertaForSequenceClassification
            self.model = RobertaForSequenceClassification.from_pretrained(str(self.model_path))
        else:
            # Charger depuis checkpoint
            checkpoint = torch.load(self.model_path, map_location=self.model_wrapper.device)
            self.model = self.model_wrapper.load_model()
            self.model.load_state_dict(checkpoint['model_state_dict'])
        
        self.model = self.model.to(self.model_wrapper.device)
        self.model.eval()
        
        logger.info(f"✅ Modèle chargé depuis: {self.model_path}")
    
    def evaluate(self, test_df: pd.DataFrame, label_encoder: LabelEncoderWrapper, 
                 batch_size: int = 32) -> Dict[str, Any]:
        """
        Évaluer le modèle sur le test set
        
        Args:
            test_df: DataFrame avec les données de test
            label_encoder: LabelEncoderWrapper pour décoder les labels
            batch_size: Taille des batches
            
        Returns:
            Dictionnaire avec toutes les métriques
        """
        logger.info("=" * 60)
        logger.info("ÉVALUATION DU MODÈLE")
        logger.info("=" * 60)
        
        # Créer le dataset et dataloader
        test_dataset = TweetDataset(
            texts=test_df['text'].tolist(),
            labels=test_df['label_encoded'].tolist(),
            tokenizer=self.model_wrapper.tokenizer,
            max_length=self.model_wrapper.max_length
        )
        
        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0
        )
        
        # Prédictions
        predictions = []
        true_labels = []
        
        logger.info("🔮 Génération des prédictions...")
        with torch.no_grad():
            for batch in test_loader:
                input_ids = batch['input_ids'].to(self.model_wrapper.device)
                attention_mask = batch['attention_mask'].to(self.model_wrapper.device)
                labels = batch['labels']
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                preds = torch.argmax(logits, dim=1)
                
                predictions.extend(preds.cpu().numpy())
                true_labels.extend(labels.numpy())
        
        # Calculer les métriques
        logger.info("📊 Calcul des métriques...")
        
        accuracy = accuracy_score(true_labels, predictions)
        f1_macro = f1_score(true_labels, predictions, average='macro')
        f1_weighted = f1_score(true_labels, predictions, average='weighted')
        f1_per_class = f1_score(true_labels, predictions, average=None)
        
        precision_macro = precision_score(true_labels, predictions, average='macro')
        precision_weighted = precision_score(true_labels, predictions, average='weighted')
        precision_per_class = precision_score(true_labels, predictions, average=None)
        
        recall_macro = recall_score(true_labels, predictions, average='macro')
        recall_weighted = recall_score(true_labels, predictions, average='weighted')
        recall_per_class = recall_score(true_labels, predictions, average=None)
        
        # Matrice de confusion
        cm = confusion_matrix(true_labels, predictions)
        
        # Classification report
        class_names = label_encoder.encoder.classes_
        report = classification_report(
            true_labels, predictions,
            target_names=class_names,
            output_dict=True
        )
        
        # Résultats
        results = {
            'accuracy': float(accuracy),
            'f1_macro': float(f1_macro),
            'f1_weighted': float(f1_weighted),
            'f1_per_class': f1_per_class.tolist(),
            'precision_macro': float(precision_macro),
            'precision_weighted': float(precision_weighted),
            'precision_per_class': precision_per_class.tolist(),
            'recall_macro': float(recall_macro),
            'recall_weighted': float(recall_weighted),
            'recall_per_class': recall_per_class.tolist(),
            'confusion_matrix': cm.tolist(),
            'classification_report': report,
            'class_names': class_names.tolist()
        }
        
        # Afficher les résultats
        logger.info("\n" + "=" * 60)
        logger.info("RÉSULTATS D'ÉVALUATION")
        logger.info("=" * 60)
        logger.info(f"📊 Accuracy: {accuracy:.4f}")
        logger.info(f"📊 F1-Score (macro): {f1_macro:.4f}")
        logger.info(f"📊 F1-Score (weighted): {f1_weighted:.4f}")
        logger.info(f"📊 Precision (macro): {precision_macro:.4f}")
        logger.info(f"📊 Recall (macro): {recall_macro:.4f}")
        
        logger.info("\n📈 Métriques par classe:")
        for i, class_name in enumerate(class_names):
            logger.info(f"   {class_name}:")
            logger.info(f"      F1: {f1_per_class[i]:.4f}")
            logger.info(f"      Precision: {precision_per_class[i]:.4f}")
            logger.info(f"      Recall: {recall_per_class[i]:.4f}")
        
        logger.info("\n📋 Classification Report:")
        logger.info(classification_report(true_labels, predictions, target_names=class_names))
        
        logger.info("=" * 60)
        
        return results
    
    def save_results(self, results: Dict[str, Any], save_path: str):
        """
        Sauvegarder les résultats d'évaluation
        
        Args:
            results: Dictionnaire avec les résultats
            save_path: Chemin où sauvegarder
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Résultats sauvegardés: {save_path}")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    
    from data_preparation import load_config
    from preprocessing import TextPreprocessor, LabelEncoderWrapper
    from data_preparation import DataLoader as DataLoaderClass
    
    logging.basicConfig(level=logging.INFO)
    
    # Charger la configuration
    config = load_config()
    
    # Charger les données de test
    test_df = pd.read_csv(f"{config['paths']['results_dir']}/test_split.csv")
    
    # Préprocessing (même que pour l'entraînement)
    preprocessor = TextPreprocessor(
        remove_urls=config['preprocessing']['remove_urls'],
        handle_mentions=config['preprocessing']['handle_mentions'],
        handle_hashtags=config['preprocessing']['handle_hashtags'],
        normalize_spaces=config['preprocessing']['normalize_spaces'],
        handle_emojis=config['preprocessing']['handle_emojis']
    )
    
    test_df = preprocessor.preprocess_dataframe(test_df, text_column='text')
    
    # Encoder les labels (doit correspondre à l'entraînement)
    label_encoder = LabelEncoderWrapper()
    label_encoder.fit(test_df['Sentiment'])
    test_df['label_encoded'] = label_encoder.transform(test_df['Sentiment'])
    
    # Évaluer
    model_path = f"{config['paths']['models_dir']}/{config['paths']['model_save_name']}"
    evaluator = ModelEvaluator(model_path, use_cuda=config['training']['use_cuda'])
    
    results = evaluator.evaluate(test_df, label_encoder, batch_size=config['training']['batch_size'])
    
    # Sauvegarder
    results_path = f"{config['paths']['results_dir']}/evaluation_results.json"
    evaluator.save_results(results, results_path)

