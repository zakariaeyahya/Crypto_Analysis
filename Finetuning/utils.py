"""
Utility functions for RoBERTa fine-tuning
"""
import os
import random
import numpy as np
import torch
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def set_seed(seed: int = 42):
    """
    Set seeds for reproducibility
    
    Args:
        seed: Seed to use
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    logger.info(f"Seed set to {seed}")


def setup_device(use_cuda: bool = True) -> torch.device:
    """
    Setup device (GPU/CPU)
    
    Args:
        use_cuda: If True, use CUDA if available
        
    Returns:
        PyTorch device
    """
    if use_cuda and torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info(f"CUDA available - Using GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        device = torch.device("cpu")
        if use_cuda:
            logger.warning("CUDA requested but not available - Using CPU")
        else:
            logger.info("Using CPU")
    
    return device


def create_directories(paths: Dict[str, str]):
    """
    Create necessary directories
    
    Args:
        paths: Dictionary with keys and directory paths
    """
    for key, path in paths.items():
        Path(path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory created/verified: {path}")


def save_config(config: Dict[str, Any], save_path: str):
    """
    Save configuration to JSON
    
    Args:
        config: Configuration dictionary
        save_path: Path where to save
    """
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    logger.info(f"Configuration saved: {save_path}")


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    logger.info(f"Configuration loaded: {config_path}")
    return config


def format_time(seconds: float) -> str:
    """
    Format time in readable format
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string (e.g., "2h 30m 15s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def get_model_size(model: torch.nn.Module) -> float:
    """
    Calculate model size in MB
    
    Args:
        model: PyTorch model
        
    Returns:
        Size in MB
    """
    param_size = 0
    buffer_size = 0
    
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()
    
    size_all_mb = (param_size + buffer_size) / 1024**2
    return size_all_mb


def count_parameters(model: torch.nn.Module) -> Dict[str, int]:
    """
    Count number of model parameters
    
    Args:
        model: PyTorch model
        
    Returns:
        Dictionary with total and trainable
    """
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    return {
        'total': total,
        'trainable': trainable,
        'frozen': total - trainable
    }
