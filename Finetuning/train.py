"""
Main training script for RoBERTa fine-tuning
"""
import os
import sys
from pathlib import Path
import yaml
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import RobertaTokenizer
import pandas as pd
import numpy as np
from tqdm import tqdm
import logging
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import set_seed, create_directories, save_config, format_time, get_model_size
from model_config import RobertaModelConfig
from data_preparation import DataLoader as DataLoaderClass, load_config
from preprocessing import TextPreprocessor, LabelEncoderWrapper, split_data

# Logging configuration
log_dir = Path(__file__).resolve().parent / 'logs'
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'training.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TweetDataset(Dataset):
    """PyTorch Dataset for tweets"""
    
    def __init__(self, texts: list, labels: list, tokenizer: RobertaTokenizer, max_length: int = 128):
        """
        Initialize dataset
        
        Args:
            texts: List of texts
            labels: List of encoded labels
            tokenizer: RoBERTa tokenizer
            max_length: Maximum sequence length
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


class Trainer:
    """Class to manage model training"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize trainer
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        self.model_config = self.config['model']
        self.data_config = self.config['data']
        self.training_config = self.config['training']
        self.paths_config = self.config['paths']
        
        # Set seed
        set_seed(self.config['reproducibility']['seed'])
        
        # Create directories
        create_directories(self.paths_config)
        
        # Initialize components
        self.model_wrapper = None
        self.label_encoder = LabelEncoderWrapper()
        self.device = None
        
        # Training metrics
        self.train_losses = []
        self.val_losses = []
        self.val_accuracies = []
        self.val_f1_scores = []
        self.best_val_f1 = 0.0
        self.best_model_path = None
        
    def prepare_data(self):
        """Load and prepare data"""
        logger.info("=" * 60)
        logger.info("DATA PREPARATION")
        logger.info("=" * 60)
        
        # Load data
        data_loader = DataLoaderClass(
            csv_path=self.data_config['csv_path'],
            sample_size=self.data_config.get('sample_size')
        )
        
        df = data_loader.load_data(chunk_size=self.data_config.get('chunk_size', 10000))
        stats = data_loader.analyze_data()
        
        # Preprocessing
        preprocessor = TextPreprocessor(
            remove_urls=self.config['preprocessing']['remove_urls'],
            handle_mentions=self.config['preprocessing']['handle_mentions'],
            handle_hashtags=self.config['preprocessing']['handle_hashtags'],
            normalize_spaces=self.config['preprocessing']['normalize_spaces'],
            handle_emojis=self.config['preprocessing']['handle_emojis']
        )
        
        df = preprocessor.preprocess_dataframe(df, text_column='text')
        
        # Encode labels
        self.label_encoder.fit(df['Sentiment'])
        df['label_encoded'] = self.label_encoder.transform(df['Sentiment'])
        
        # Split data
        train_df, val_df, test_df = split_data(
            df,
            text_column='text',
            label_column='Sentiment',
            train_size=self.data_config['train_split'],
            val_size=self.data_config['val_split'],
            test_size=self.data_config['test_split'],
            stratify=self.data_config.get('stratify', True),
            random_state=self.config['reproducibility']['seed']
        )
        
        # Save splits
        train_df.to_csv(f"{self.paths_config['results_dir']}/train_split.csv", index=False)
        val_df.to_csv(f"{self.paths_config['results_dir']}/val_split.csv", index=False)
        test_df.to_csv(f"{self.paths_config['results_dir']}/test_split.csv", index=False)
        
        logger.info("Data prepared and saved")
        
        return train_df, val_df, test_df
    
    def create_dataloaders(self, train_df: pd.DataFrame, val_df: pd.DataFrame):
        """Create PyTorch DataLoaders"""
        logger.info("Creating DataLoaders...")
        
        # Create datasets
        train_dataset = TweetDataset(
            texts=train_df['text'].tolist(),
            labels=train_df['label_encoded'].tolist(),
            tokenizer=self.model_wrapper.tokenizer,
            max_length=self.model_config['max_length']
        )
        
        val_dataset = TweetDataset(
            texts=val_df['text'].tolist(),
            labels=val_df['label_encoded'].tolist(),
            tokenizer=self.model_wrapper.tokenizer,
            max_length=self.model_config['max_length']
        )
        
        # Create DataLoaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.training_config['batch_size'],
            shuffle=True,
            num_workers=0  # Set to 0 for Windows
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.training_config['batch_size'],
            shuffle=False,
            num_workers=0
        )
        
        logger.info(f"DataLoaders created (train: {len(train_loader)} batches, val: {len(val_loader)} batches)")
        
        return train_loader, val_loader
    
    def train_epoch(self, model, train_loader, optimizer, scheduler, criterion, device, use_fp16: bool = False):
        """Train for one epoch"""
        model.train()
        total_loss = 0
        num_batches = 0
        
        # Mixed precision training
        scaler = torch.cuda.amp.GradScaler() if use_fp16 and device.type == 'cuda' else None
        
        progress_bar = tqdm(train_loader, desc="Training")
        
        for batch in progress_bar:
            # Move to device
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            optimizer.zero_grad()
            
            # Forward pass with mixed precision if enabled
            if scaler is not None:
                with torch.cuda.amp.autocast():
                    outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                    loss = outputs.loss
                
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), self.training_config['max_grad_norm'])
                scaler.step(optimizer)
                scaler.update()
            else:
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), self.training_config['max_grad_norm'])
                optimizer.step()
            
            scheduler.step()
            
            total_loss += loss.item()
            num_batches += 1
            
            # Update progress bar
            progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        avg_loss = total_loss / num_batches
        return avg_loss
    
    def validate(self, model, val_loader, criterion, device):
        """Validate the model"""
        model.eval()
        total_loss = 0
        predictions = []
        true_labels = []
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validation"):
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                
                total_loss += loss.item()
                
                # Predictions
                logits = outputs.logits
                preds = torch.argmax(logits, dim=1)
                
                predictions.extend(preds.cpu().numpy())
                true_labels.extend(labels.cpu().numpy())
        
        avg_loss = total_loss / len(val_loader)
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, f1_score
        
        accuracy = accuracy_score(true_labels, predictions)
        f1 = f1_score(true_labels, predictions, average='macro')
        
        return avg_loss, accuracy, f1
    
    def save_checkpoint(self, model, epoch: int, val_f1: float, is_best: bool = False):
        """Save a checkpoint"""
        checkpoint_dir = Path(self.paths_config['checkpoints_dir'])
        
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'val_f1': val_f1,
            'config': self.config
        }
        
        # Save regular checkpoint
        checkpoint_path = checkpoint_dir / f"checkpoint_epoch_{epoch}.pt"
        torch.save(checkpoint, checkpoint_path)
        
        # Save best model
        if is_best:
            best_path = checkpoint_dir / "best_model.pt"
            torch.save(checkpoint, best_path)
            self.best_model_path = best_path
            logger.info(f"Best model saved: {best_path}")
    
    def train(self):
        """Main training function"""
        logger.info("=" * 60)
        logger.info("STARTING TRAINING")
        logger.info("=" * 60)
        
        # Prepare data
        train_df, val_df, test_df = self.prepare_data()
        
        # Initialize model
        logger.info("\n" + "=" * 60)
        logger.info("MODEL INITIALIZATION")
        logger.info("=" * 60)
        
        self.model_wrapper = RobertaModelConfig(
            model_name=self.model_config['name'],
            num_labels=self.model_config['num_labels'],
            max_length=self.model_config['max_length'],
            freeze_layers=self.model_config.get('freeze_layers', False),
            use_cuda=self.training_config.get('use_cuda', True)
        )
        
        self.model_wrapper.load_tokenizer()
        model = self.model_wrapper.load_model()
        self.device = self.model_wrapper.device
        
        # Create DataLoaders
        train_loader, val_loader = self.create_dataloaders(train_df, val_df)
        
        # Configure optimizer and scheduler
        num_training_steps = len(train_loader) * self.training_config['num_epochs']
        
        optimizer = self.model_wrapper.get_optimizer(
            learning_rate=self.training_config['learning_rate'],
            weight_decay=self.training_config['weight_decay']
        )
        
        scheduler = self.model_wrapper.get_scheduler(
            optimizer,
            num_training_steps=num_training_steps,
            warmup_steps=self.training_config['warmup_steps']
        )
        
        # Loss function
        criterion = nn.CrossEntropyLoss()
        
        # Early stopping
        early_stopping_config = self.training_config.get('early_stopping', {})
        patience = early_stopping_config.get('patience', 3) if early_stopping_config.get('enabled', False) else None
        patience_counter = 0
        
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING")
        logger.info("=" * 60)
        logger.info(f"Epochs: {self.training_config['num_epochs']}")
        logger.info(f"Batch size: {self.training_config['batch_size']}")
        logger.info(f"Learning rate: {self.training_config['learning_rate']}")
        logger.info(f"Device: {self.device}")
        logger.info(f"FP16: {self.training_config.get('use_fp16', False)}")
        logger.info("=" * 60 + "\n")
        
        start_time = datetime.now()
        
        # Training loop
        for epoch in range(1, self.training_config['num_epochs'] + 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"EPOCH {epoch}/{self.training_config['num_epochs']}")
            logger.info(f"{'='*60}")
            
            # Training
            train_loss = self.train_epoch(
                model, train_loader, optimizer, scheduler, criterion, 
                self.device, use_fp16=self.training_config.get('use_fp16', False)
            )
            self.train_losses.append(train_loss)
            
            # Validation
            val_loss, val_accuracy, val_f1 = self.validate(model, val_loader, criterion, self.device)
            self.val_losses.append(val_loss)
            self.val_accuracies.append(val_accuracy)
            self.val_f1_scores.append(val_f1)
            
            logger.info(f"\nEpoch {epoch} Metrics:")
            logger.info(f"   Train Loss: {train_loss:.4f}")
            logger.info(f"   Val Loss: {val_loss:.4f}")
            logger.info(f"   Val Accuracy: {val_accuracy:.4f}")
            logger.info(f"   Val F1-Score: {val_f1:.4f}")
            
            # Save checkpoint
            is_best = val_f1 > self.best_val_f1
            if is_best:
                self.best_val_f1 = val_f1
                patience_counter = 0
            else:
                patience_counter += 1
            
            self.save_checkpoint(model, epoch, val_f1, is_best=is_best)
            
            # Early stopping
            if patience and patience_counter >= patience:
                logger.info(f"\nEarly stopping triggered (patience={patience})")
                break
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING COMPLETED")
        logger.info("=" * 60)
        logger.info(f"Total duration: {format_time(duration)}")
        logger.info(f"Best F1-Score: {self.best_val_f1:.4f}")
        logger.info(f"Best model: {self.best_model_path}")
        
        # Save final model
        model_save_path = Path(self.paths_config['models_dir']) / self.paths_config['model_save_name']
        model.save_pretrained(model_save_path)
        self.model_wrapper.tokenizer.save_pretrained(model_save_path)
        logger.info(f"Final model saved: {model_save_path}")
        
        # Save metrics
        metrics = {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'val_accuracies': self.val_accuracies,
            'val_f1_scores': self.val_f1_scores,
            'best_val_f1': self.best_val_f1,
            'training_time_seconds': duration
        }
        
        metrics_path = Path(self.paths_config['results_dir']) / 'training_metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Metrics saved: {metrics_path}")


if __name__ == "__main__":
    trainer = Trainer()
    trainer.train()

