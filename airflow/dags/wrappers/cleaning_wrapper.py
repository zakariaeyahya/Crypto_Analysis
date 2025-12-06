"""
Wrapper for Reddit Dataset Cleaning script
"""
import logging
import sys
import json
from pathlib import Path

logger = logging.getLogger(__name__)


def run_reddit_cleaning(**context):
    """
    Run Reddit dataset cleaning script
    
    Returns:
        Dictionary with cleaning statistics
    """
    logger.info("Starting Reddit dataset cleaning...")
    
    # Import the cleaning script as a module
    script_path = Path("/opt/airflow/data_cleaning/Script/Reddit-Dataset-Cleaning.py")
    
    if not script_path.exists():
        # Try relative path
        script_path = Path(__file__).parent.parent.parent.parent / "data_cleaning" / "Script" / "Reddit-Dataset-Cleaning.py"
    
    if not script_path.exists():
        raise FileNotFoundError(f"Cleaning script not found: {script_path}")
    
    # Read the master dataset to get initial count
    master_path = Path("data_consolidation/outputs/master_dataset.csv")
    if not master_path.exists():
        raise FileNotFoundError(f"Master dataset not found: {master_path}")
    
    import pandas as pd
    initial_df = pd.read_csv(master_path)
    initial_rows = len(initial_df)
    
    # Execute the cleaning script
    # Since the script is designed to be run directly, we'll import and call its main function
    # or execute it as a subprocess
    
    try:
        # Add script directory to path
        script_dir = script_path.parent
        sys.path.insert(0, str(script_dir))
        
        # Import and execute the cleaning logic
        # The script modifies global variables, so we need to execute it carefully
        import subprocess
        import os
        
        # Change to script directory and execute
        original_dir = os.getcwd()
        try:
            os.chdir(script_dir)
            result = subprocess.run(
                [sys.executable, script_path.name],
                capture_output=True,
                text=True,
                timeout=900  # 15 minutes timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Cleaning script failed: {result.stderr}")
                raise RuntimeError(f"Cleaning script failed: {result.stderr}")
            
            logger.info("Cleaning script executed successfully")
        finally:
            os.chdir(original_dir)
        
    except Exception as e:
        logger.error(f"Error executing cleaning script: {e}")
        raise
    
    # Read the cleaned dataset and summary
    cleaned_path = Path("data/silver/reddit/cleaned_reddit_dataset.csv")
    summary_path = Path("data/silver/reddit/summary.json")
    
    if not cleaned_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {cleaned_path}")
    
    final_df = pd.read_csv(cleaned_path)
    final_rows = len(final_df)
    
    removed_rows = initial_rows - final_rows
    removal_rate = (removed_rows / initial_rows * 100) if initial_rows > 0 else 0
    
    # Load summary if available
    breakdown = {}
    if summary_path.exists():
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                breakdown = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load summary: {e}")
    
    result = {
        'initial_rows': initial_rows,
        'final_rows': final_rows,
        'removed_rows': removed_rows,
        'removal_rate': removal_rate,
        'breakdown': breakdown
    }
    
    logger.info(f"Cleaning completed: {initial_rows} -> {final_rows} rows ({removal_rate:.2f}% removed)")
    
    return result


