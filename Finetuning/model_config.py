"""
RoBERTa model configuration and loading
"""
import torch
from torch.optim import AdamW
from transformers import (
    RobertaForSequenceClassification,
    RobertaTokenizer,
    RobertaConfig,
    get_linear_schedule_with_warmup
)
from typing import Dict, Any, Tuple
import logging

from utils import setup_device, count_parameters

logger = logging.getLogger(__name__)


class RobertaModelConfig:
    """Class to configure and load RoBERTa model"""
    
    def __init__(self, 
                 model_name: str = "cardiffnlp/twitter-roberta-base-sentiment",
                 num_labels: int = 3,
                 max_length: int = 128,
                 freeze_layers: bool = False,
                 use_cuda: bool = True):
        """
        Initialize model configuration
        
        Args:
            model_name: Hugging Face model name
            num_labels: Number of output classes
            max_length: Maximum sequence length
            freeze_layers: If True, freeze first layers
            use_cuda: Use CUDA if available
        """
        self.model_name = model_name
        self.num_labels = num_labels
        self.max_length = max_length
        self.freeze_layers = freeze_layers
        self.device = setup_device(use_cuda)
        
        self.model = None
        self.tokenizer = None
        
    def load_tokenizer(self):
        """Load RoBERTa tokenizer"""
        logger.info(f"Loading tokenizer: {self.model_name}")
        self.tokenizer = RobertaTokenizer.from_pretrained(self.model_name)
        logger.info(f"Tokenizer loaded (vocab size: {len(self.tokenizer)})")
        return self.tokenizer
    
    def load_model(self):
        """
        Load RoBERTa model for sequence classification
        
        Returns:
            Configured model
        """
        logger.info(f"Loading model: {self.model_name}")
        logger.info(f"   Classes: {self.num_labels}")
        logger.info(f"   Device: {self.device}")
        
        # Load model
        self.model = RobertaForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=self.num_labels
        )
        
        # Freeze some layers if requested
        if self.freeze_layers:
            logger.info("Freezing first layers of RoBERTa...")
            # Freeze embeddings and first layers
            for param in self.model.roberta.embeddings.parameters():
                param.requires_grad = False
            
            # Freeze first 6 attention layers
            for i in range(6):
                for param in self.model.roberta.encoder.layer[i].parameters():
                    param.requires_grad = False
            
            logger.info("First layers frozen")
        
        # Move model to device
        self.model = self.model.to(self.device)
        
        # Display model statistics
        params = count_parameters(self.model)
        logger.info(f"Model parameters:")
        logger.info(f"   Total: {params['total']:,}")
        logger.info(f"   Trainable: {params['trainable']:,}")
        logger.info(f"   Frozen: {params['frozen']:,}")
        
        # Training mode
        self.model.train()
        
        logger.info("Model loaded and configured")
        
        return self.model
    
    def get_optimizer(self, learning_rate: float = 2e-5, weight_decay: float = 0.01):
        """
        Create AdamW optimizer
        
        Args:
            learning_rate: Learning rate
            weight_decay: Weight decay
            
        Returns:
            Configured optimizer
        """
        if self.model is None:
            raise ValueError("Model must be loaded first")
        
        # Parameters to optimize (only those requiring gradients)
        param_optimizer = list(self.model.named_parameters())
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {
                'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
                'weight_decay': weight_decay
            },
            {
                'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)],
                'weight_decay': 0.0
            }
        ]
        
        optimizer = AdamW(optimizer_grouped_parameters, lr=learning_rate)
        logger.info(f"AdamW optimizer created (lr={learning_rate}, weight_decay={weight_decay})")
        
        return optimizer
    
    def get_scheduler(self, optimizer, num_training_steps: int, warmup_steps: int = 1000):
        """
        Create scheduler with warmup
        
        Args:
            optimizer: Optimizer
            num_training_steps: Total number of training steps
            warmup_steps: Number of warmup steps
            
        Returns:
            Configured scheduler
        """
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=num_training_steps
        )
        logger.info(f"Scheduler created (warmup_steps={warmup_steps}, total_steps={num_training_steps})")
        
        return scheduler
    
    def tokenize_texts(self, texts: list, padding: bool = True, truncation: bool = True):
        """
        Tokenize a list of texts
        
        Args:
            texts: List of texts to tokenize
            padding: Add padding
            truncation: Truncate sequences that are too long
            
        Returns:
            Dictionary with input_ids and attention_mask
        """
        if self.tokenizer is None:
            raise ValueError("Tokenizer must be loaded first")
        
        return self.tokenizer(
            texts,
            padding=padding,
            truncation=truncation,
            max_length=self.max_length,
            return_tensors="pt"
        )
    
    def get_class_weights(self, train_labels: torch.Tensor) -> torch.Tensor:
        """
        Calculate class weights to handle imbalance
        
        Args:
            train_labels: Tensor with training labels
            
        Returns:
            Tensor with class weights
        """
        from collections import Counter
        
        label_counts = Counter(train_labels.cpu().numpy())
        total = len(train_labels)
        
        # Calculate weights inversely proportional to frequency
        weights = torch.zeros(self.num_labels, device=self.device)
        for label, count in label_counts.items():
            weights[label] = total / (self.num_labels * count)
        
        # Normalize
        weights = weights / weights.sum() * self.num_labels
        
        logger.info(f"Class weights calculated: {weights.cpu().tolist()}")
        
        return weights
