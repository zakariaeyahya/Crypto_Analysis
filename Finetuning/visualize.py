"""
Visualizations for training and evaluation results
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Style configuration
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def plot_training_curves(metrics_path: str, save_path: str = None):
    """
    Visualize training curves (loss, accuracy, F1)
    
    Args:
        metrics_path: Path to JSON metrics file
        save_path: Path where to save the figure
    """
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    
    epochs = range(1, len(metrics['train_losses']) + 1)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Loss
    axes[0].plot(epochs, metrics['train_losses'], 'b-', label='Train Loss', linewidth=2)
    axes[0].plot(epochs, metrics['val_losses'], 'r-', label='Val Loss', linewidth=2)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss', fontsize=12)
    axes[0].set_title('Training and Validation Loss', fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=11)
    axes[0].grid(True, alpha=0.3)
    
    # Accuracy
    axes[1].plot(epochs, metrics['val_accuracies'], 'g-', label='Val Accuracy', linewidth=2)
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Accuracy', fontsize=12)
    axes[1].set_title('Validation Accuracy', fontsize=14, fontweight='bold')
    axes[1].legend(fontsize=11)
    axes[1].grid(True, alpha=0.3)
    
    # F1-Score
    axes[2].plot(epochs, metrics['val_f1_scores'], 'm-', label='Val F1-Score', linewidth=2)
    axes[2].set_xlabel('Epoch', fontsize=12)
    axes[2].set_ylabel('F1-Score', fontsize=12)
    axes[2].set_title('Validation F1-Score', fontsize=14, fontweight='bold')
    axes[2].legend(fontsize=11)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Figure saved: {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_confusion_matrix(results_path: str, save_path: str = None):
    """
    Visualize confusion matrix
    
    Args:
        results_path: Path to JSON results file
        save_path: Path where to save the figure
    """
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    cm = np.array(results['confusion_matrix'])
    class_names = results['class_names']
    
    # Normalize matrix
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Absolute confusion matrix
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names,
                ax=axes[0], cbar_kws={'label': 'Count'})
    axes[0].set_xlabel('Predicted', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('True', fontsize=12, fontweight='bold')
    axes[0].set_title('Confusion Matrix (Absolute)', fontsize=14, fontweight='bold')
    
    # Normalized confusion matrix
    sns.heatmap(cm_normalized, annot=True, fmt='.2%', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names,
                ax=axes[1], cbar_kws={'label': 'Percentage'})
    axes[1].set_xlabel('Predicted', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('True', fontsize=12, fontweight='bold')
    axes[1].set_title('Confusion Matrix (Normalized)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Figure saved: {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_metrics_comparison(results_path: str, save_path: str = None):
    """
    Visualize metrics comparison by class
    
    Args:
        results_path: Path to JSON results file
        save_path: Path where to save the figure
    """
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    class_names = results['class_names']
    f1_scores = results['f1_per_class']
    precision_scores = results['precision_per_class']
    recall_scores = results['recall_per_class']
    
    x = np.arange(len(class_names))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars1 = ax.bar(x - width, f1_scores, width, label='F1-Score', alpha=0.8)
    bars2 = ax.bar(x, precision_scores, width, label='Precision', alpha=0.8)
    bars3 = ax.bar(x + width, recall_scores, width, label='Recall', alpha=0.8)
    
    ax.set_xlabel('Classes', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Metrics Comparison by Class', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(class_names)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim([0, 1.1])
    
    # Add values on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Figure saved: {save_path}")
    else:
        plt.show()
    
    plt.close()


def create_all_visualizations(results_dir: str):
    """
    Create all visualizations from results
    
    Args:
        results_dir: Directory containing result files
    """
    results_dir = Path(results_dir)
    
    # Training curves
    metrics_path = results_dir / "training_metrics.json"
    if metrics_path.exists():
        plot_training_curves(
            str(metrics_path),
            str(results_dir / "training_curves.png")
        )
    
    # Confusion matrix and metrics
    eval_path = results_dir / "evaluation_results.json"
    if eval_path.exists():
        plot_confusion_matrix(
            str(eval_path),
            str(results_dir / "confusion_matrix.png")
        )
        plot_metrics_comparison(
            str(eval_path),
            str(results_dir / "metrics_comparison.png")
        )
    
    logger.info("All visualizations created")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    
    from data_preparation import load_config
    
    logging.basicConfig(level=logging.INFO)
    
    config = load_config()
    results_dir = config['paths']['results_dir']
    
    create_all_visualizations(results_dir)

