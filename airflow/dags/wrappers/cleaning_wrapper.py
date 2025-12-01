"""
Wrapper for Reddit Dataset Cleaning script
Now uses the modular clean_reddit_data() function from Reddit-Dataset-Cleaning.py
"""
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def run_reddit_cleaning(**context):
    """
    Run Reddit dataset cleaning by calling the clean_reddit_data() function

    Args:
        **context: Airflow context containing execution_date

    Returns:
        Dictionary with cleaning statistics
    """
    logger.info("Starting Reddit dataset cleaning...")

    # Get execution_date from Airflow context
    execution_date = context.get('execution_date')

    if execution_date is None:
        logger.warning("No execution_date found in context - using current date")
        from datetime import datetime
        execution_date = datetime.now()

    logger.info(f"Cleaning data for execution_date: {execution_date.strftime('%Y-%m-%d')}")

    # Import the cleaning function
    script_path = Path("/opt/airflow/data_cleaning/Script/Reddit-Dataset-Cleaning.py")

    if not script_path.exists():
        # Try relative path (for local development)
        script_path = Path(__file__).parent.parent.parent.parent / "data_cleaning" / "Script" / "Reddit-Dataset-Cleaning.py"

    if not script_path.exists():
        raise FileNotFoundError(f"Cleaning script not found: {script_path}")

    # Add script directory to path
    script_dir = script_path.parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    try:
        # Import the cleaning module
        import importlib.util
        spec = importlib.util.spec_from_file_location("reddit_cleaning", script_path)
        cleaning_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cleaning_module)

        # Call the clean_reddit_data function with execution_date
        logger.info("Calling clean_reddit_data() function...")
        result = cleaning_module.clean_reddit_data(execution_date=execution_date)

        logger.info(f"Cleaning completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error during cleaning: {e}")
        raise




