"""
Helper functions for Airflow DAGs
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def check_file_exists(path: Path) -> bool:
    """
    Check if a file exists
    
    Args:
        path: Path to check
        
    Returns:
        True if file exists, False otherwise
    """
    exists = path.exists()
    if not exists:
        logger.warning(f"File not found: {path}")
    return exists


def load_checkpoint(checkpoint_file: Path) -> Dict[str, Any]:
    """
    Load checkpoint file with metadata
    
    Args:
        checkpoint_file: Path to checkpoint JSON file
        
    Returns:
        Dictionary with checkpoint data, empty dict if file doesn't exist
    """
    if not checkpoint_file.exists():
        logger.info(f"Checkpoint file not found: {checkpoint_file}. Starting fresh.")
        return {}
    
    try:
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
            logger.info(f"Loaded checkpoint from {checkpoint_file}")
            return checkpoint
    except Exception as e:
        logger.error(f"Failed to load checkpoint: {e}")
        return {}


def save_checkpoint(checkpoint_file: Path, data: Dict[str, Any]) -> bool:
    """
    Save checkpoint file with metadata
    
    Args:
        checkpoint_file: Path to checkpoint JSON file
        data: Dictionary to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Checkpoint saved to {checkpoint_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to save checkpoint: {e}")
        return False


def save_metrics_to_xcom(context: Dict[str, Any], metrics: Dict[str, Any]) -> None:
    """
    Save metrics to XCom for downstream tasks
    
    Args:
        context: Airflow context dictionary
        metrics: Dictionary of metrics to save
    """
    from airflow.models import TaskInstance
    ti = context['ti']
    
    for key, value in metrics.items():
        ti.xcom_push(key=key, value=value)
        logger.info(f"Saved metric to XCom: {key} = {value}")


def validate_dataframe_schema(df, required_columns: list) -> bool:
    """
    Validate that DataFrame has required columns
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        True if all columns present, False otherwise
    """
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        logger.error(f"Missing required columns: {missing}")
        return False
    logger.info(f"Schema validation passed. All required columns present: {required_columns}")
    return True


def is_checkpoint_recent(checkpoint_file: Path, validity_days: int = 7) -> bool:
    """
    Check if checkpoint is recent enough (within validity_days)
    
    Args:
        checkpoint_file: Path to checkpoint file
        validity_days: Number of days checkpoint is valid
        
    Returns:
        True if checkpoint is recent, False otherwise
    """
    if not checkpoint_file.exists():
        return False
    
    try:
        checkpoint = load_checkpoint(checkpoint_file)
        if 'last_updated' in checkpoint:
            last_updated = datetime.fromisoformat(checkpoint['last_updated'])
            age = datetime.now() - last_updated
            is_recent = age.days < validity_days
            logger.info(f"Checkpoint age: {age.days} days. Valid: {is_recent}")
            return is_recent
        return False
    except Exception as e:
        logger.error(f"Error checking checkpoint age: {e}")
        return False


def detect_kaggle_data() -> Dict[str, Any]:
    """
    Detect if Kaggle data is available in bronze layer
    
    Returns:
        Dictionary with detection results:
        - available: bool
        - file_count: int
        - files: list of file paths
        - path: str
    """
    kaggle_path = Path("data/bronze/kaggle")
    
    if not kaggle_path.exists():
        logger.info("Kaggle data directory does not exist")
        return {
            'available': False,
            'file_count': 0,
            'files': [],
            'path': str(kaggle_path)
        }
    
    # Look for CSV files
    csv_files = list(kaggle_path.glob("*.csv"))
    
    result = {
        'available': len(csv_files) > 0,
        'file_count': len(csv_files),
        'files': [str(f) for f in csv_files],
        'path': str(kaggle_path)
    }
    
    if result['available']:
        logger.info(f"Kaggle data detected: {result['file_count']} CSV file(s) found")
        logger.info(f"Files: {[Path(f).name for f in result['files']]}")
    else:
        logger.info("No Kaggle data detected (this is normal - Kaggle is optional)")
    
    return result


