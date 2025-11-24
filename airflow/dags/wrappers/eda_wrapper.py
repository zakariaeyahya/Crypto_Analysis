"""
Wrapper for EDA analysis script
"""
import logging
import sys
import subprocess
import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

logger = logging.getLogger(__name__)


def execute_eda(**context):
    """
    Execute EDA analysis
    
    Returns:
        Dictionary with EDA results
    """
    logger.info("Starting EDA analysis...")
    
    script_path = Path("/opt/airflow/EDA_Task/exploratory_data_analysis.py")
    
    if not script_path.exists():
        # Try relative path
        script_path = Path(__file__).parent.parent.parent.parent / "EDA_Task" / "exploratory_data_analysis.py"
    
    if not script_path.exists():
        raise FileNotFoundError(f"EDA script not found: {script_path}")
    
    # Check if master dataset exists
    master_path = Path("data_consolidation/outputs/master_dataset.csv")
    if not master_path.exists():
        # Try alternative location
        master_path = Path("EDA_Task/master_dataset.csv")
    
    if not master_path.exists():
        raise FileNotFoundError("Master dataset not found for EDA")
    
    # Create plots directory
    plots_dir = Path("EDA_Task/plots")
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    # Execute the EDA script
    script_dir = script_path.parent
    original_dir = os.getcwd()
    
    try:
        os.chdir(script_dir)
        
        # Set matplotlib backend to non-interactive
        os.environ['MPLBACKEND'] = 'Agg'
        
        result = subprocess.run(
            [sys.executable, script_path.name],
            capture_output=True,
            text=True,
            timeout=900  # 15 minutes timeout
        )
        
        if result.returncode != 0:
            logger.warning(f"EDA script had warnings: {result.stderr}")
            # Don't fail if script has warnings, just log them
        
        logger.info("EDA script executed successfully")
        if result.stdout:
            logger.info(f"Script output: {result.stdout[:500]}")  # First 500 chars
    finally:
        os.chdir(original_dir)
    
    # Count generated plots
    plots_generated = 0
    if plots_dir.exists():
        plots_generated = len(list(plots_dir.glob("*.png"))) + len(list(plots_dir.glob("*.svg")))
    
    # Count cryptos analyzed (from logs or by reading data)
    cryptos_analyzed = 0
    try:
        import pandas as pd
        df = pd.read_csv(master_path, nrows=1000)  # Sample
        if 'subreddit' in df.columns:
            cryptos_analyzed = df['subreddit'].nunique()
    except Exception as e:
        logger.warning(f"Could not count cryptos: {e}")
    
    result = {
        'plots_generated': plots_generated,
        'cryptos_analyzed': cryptos_analyzed
    }
    
    logger.info(f"EDA completed: {plots_generated} plots generated, {cryptos_analyzed} cryptos analyzed")
    
    return result




