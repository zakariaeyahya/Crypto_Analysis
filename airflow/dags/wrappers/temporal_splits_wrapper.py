"""
Wrapper for Temporal Splits creation script
"""
import logging
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def run_temporal_split_creation(**context):
    """
    Run temporal splits creation script
    
    Returns:
        Dictionary with split statistics
    """
    logger.info("Starting temporal splits creation...")
    
    script_path = Path("/opt/airflow/data_cleaning/Script/CreateTemporalSplits.py")
    
    if not script_path.exists():
        # Try relative path
        script_path = Path(__file__).parent.parent.parent.parent / "data_cleaning" / "Script" / "CreateTemporalSplits.py"
    
    if not script_path.exists():
        raise FileNotFoundError(f"Temporal splits script not found: {script_path}")
    
    # Execute the script
    script_dir = script_path.parent
    original_dir = os.getcwd()
    
    try:
        os.chdir(script_dir)
        result = subprocess.run(
            [sys.executable, script_path.name],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Temporal splits script failed: {result.stderr}")
            raise RuntimeError(f"Temporal splits script failed: {result.stderr}")
        
        logger.info("Temporal splits script executed successfully")
        if result.stdout:
            logger.info(f"Script output: {result.stdout}")
    finally:
        os.chdir(original_dir)
    
    # Read the generated splits
    output_dir = Path("data/silver/reddit")
    train_path = output_dir / "train_data.csv"
    val_path = output_dir / "validation_data.csv"
    test_path = output_dir / "test_data.csv"
    
    import pandas as pd
    
    train_rows = 0
    val_rows = 0
    test_rows = 0
    window_start = None
    window_end = None
    
    if train_path.exists():
        train_df = pd.read_csv(train_path)
        train_rows = len(train_df)
        if 'created_date' in train_df.columns:
            train_df['created_date'] = pd.to_datetime(train_df['created_date'], errors='coerce')
            window_start = train_df['created_date'].min()
    
    if val_path.exists():
        val_df = pd.read_csv(val_path)
        val_rows = len(val_df)
    
    if test_path.exists():
        test_df = pd.read_csv(test_path)
        test_rows = len(test_df)
        if 'created_date' in test_df.columns:
            test_df['created_date'] = pd.to_datetime(test_df['created_date'], errors='coerce')
            window_end = test_df['created_date'].max()
    
    result = {
        'train_rows': train_rows,
        'val_rows': val_rows,
        'test_rows': test_rows,
        'window_start': str(window_start) if window_start else None,
        'window_end': str(window_end) if window_end else None
    }
    
    logger.info(f"Splits created: Train={train_rows}, Val={val_rows}, Test={test_rows}")
    
    return result


