"""
Validation functions for data quality checks
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_bronze_data(execution_date: datetime, data_type: str = 'reddit') -> Dict[str, Any]:
    """
    Validate bronze layer data exists for execution date
    
    Args:
        execution_date: Date to check
        data_type: Type of data ('reddit' or 'kaggle')
        
    Returns:
        Dictionary with validation results
    """
    year = execution_date.strftime('%Y')
    month = execution_date.strftime('%m')
    day = execution_date.strftime('%d')
    
    if data_type == 'reddit':
        bronze_path = Path(f"data/bronze/reddit/year={year}/month={month}/day={day}")
        csv_files = list(bronze_path.glob("*.csv"))
    else:  # kaggle
        bronze_path = Path("data/bronze/kaggle")
        csv_files = list(bronze_path.glob("*.csv"))
    
    result = {
        'exists': len(csv_files) > 0,
        'file_count': len(csv_files),
        'files': [str(f) for f in csv_files],
        'path': str(bronze_path)
    }
    
    if result['exists']:
        logger.info(f"Bronze data found: {result['file_count']} files in {bronze_path}")
    else:
        logger.warning(f"No bronze data found in {bronze_path}")
    
    return result


def validate_silver_data(execution_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Validate silver layer data
    
    Args:
        execution_date: Optional date to check (not used for silver, kept for consistency)
        
    Returns:
        Dictionary with validation results
    """
    silver_path = Path("data/silver/reddit/cleaned_reddit_dataset.csv")
    
    result = {
        'exists': silver_path.exists(),
        'file_path': str(silver_path)
    }
    
    if result['exists']:
        try:
            df = pd.read_csv(silver_path, nrows=1000)  # Sample read
            result['has_data'] = len(df) > 0
            result['columns'] = list(df.columns)
            result['sample_rows'] = len(df)
            logger.info(f"Silver data validated: {len(df)} sample rows, {len(df.columns)} columns")
        except Exception as e:
            logger.error(f"Error reading silver data: {e}")
            result['has_data'] = False
            result['error'] = str(e)
    else:
        logger.warning(f"Silver data file not found: {silver_path}")
        result['has_data'] = False
    
    return result


def validate_gold_data() -> Dict[str, Any]:
    """
    Validate gold layer data
    
    Returns:
        Dictionary with validation results
    """
    gold_path = Path("data/gold/eda")
    
    result = {
        'exists': gold_path.exists(),
        'path': str(gold_path),
        'files': []
    }
    
    if result['exists']:
        result['files'] = [f.name for f in gold_path.iterdir() if f.is_file()]
        logger.info(f"Gold data found: {len(result['files'])} files")
    else:
        logger.warning(f"Gold data directory not found: {gold_path}")
    
    return result


def check_data_quality_thresholds(df: pd.DataFrame, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check data quality against thresholds
    
    Args:
        df: DataFrame to check
        thresholds: Dictionary with threshold values
        
    Returns:
        Dictionary with quality check results
    """
    results = {
        'passed': True,
        'checks': {}
    }
    
    # Check minimum rows
    if 'min_rows' in thresholds:
        min_rows = thresholds['min_rows']
        has_enough = len(df) >= min_rows
        results['checks']['min_rows'] = {
            'passed': has_enough,
            'expected': min_rows,
            'actual': len(df)
        }
        if not has_enough:
            results['passed'] = False
            logger.warning(f"Failed min_rows check: {len(df)} < {min_rows}")
    
    # Check required columns
    if 'required_columns' in thresholds:
        required = thresholds['required_columns']
        missing = [col for col in required if col not in df.columns]
        results['checks']['required_columns'] = {
            'passed': len(missing) == 0,
            'missing': missing
        }
        if missing:
            results['passed'] = False
            logger.warning(f"Missing required columns: {missing}")
    
    # Check null percentage
    if 'max_null_percentage' in thresholds:
        max_null_pct = thresholds['max_null_percentage']
        null_pct = (df.isnull().sum() / len(df) * 100).max()
        passed = null_pct <= max_null_pct
        results['checks']['null_percentage'] = {
            'passed': passed,
            'max_allowed': max_null_pct,
            'actual_max': null_pct
        }
        if not passed:
            results['passed'] = False
            logger.warning(f"Null percentage too high: {null_pct:.2f}% > {max_null_pct}%")
    
    if results['passed']:
        logger.info("All data quality checks passed")
    
    return results


def validate_kaggle_download(file_path: Path, min_records: int = 10000000) -> Dict[str, Any]:
    """
    Validate downloaded Kaggle dataset
    
    Args:
        file_path: Path to downloaded CSV
        min_records: Minimum number of records expected
        
    Returns:
        Dictionary with validation results
    """
    result = {
        'validation_status': 'failed',
        'records': 0,
        'columns': [],
        'errors': []
    }
    
    if not file_path.exists():
        result['errors'].append(f"File not found: {file_path}")
        return result
    
    try:
        # Sample read to check structure
        df_sample = pd.read_csv(file_path, nrows=1000)
        result['columns'] = list(df_sample.columns)
        
        # Check required columns
        required_cols = ['tweet', 'sentiment', 'timestamp']
        missing = [col for col in required_cols if col not in df_sample.columns]
        if missing:
            result['errors'].append(f"Missing required columns: {missing}")
        
        # Count total records (this might be slow for large files)
        logger.info("Counting total records in Kaggle dataset...")
        df_full = pd.read_csv(file_path)
        result['records'] = len(df_full)
        
        if result['records'] < min_records:
            result['errors'].append(f"Record count {result['records']} < minimum {min_records}")
        
        if not result['errors']:
            result['validation_status'] = 'passed'
            logger.info(f"Kaggle dataset validation passed: {result['records']} records")
        else:
            logger.error(f"Kaggle dataset validation failed: {result['errors']}")
            
    except Exception as e:
        result['errors'].append(f"Error reading file: {str(e)}")
        logger.error(f"Validation error: {e}")
    
    return result


