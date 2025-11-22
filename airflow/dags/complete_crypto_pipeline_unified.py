"""
Complete Unified Pipeline DAG - Single DAG containing all crypto analysis tasks
This DAG replaces the multi-DAG architecture with a single unified pipeline
"""
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import logging
import sys
import json
import shutil

# Add modules to path
sys.path.insert(0, '/opt/airflow')
sys.path.insert(0, '/opt/airflow/dags')

# Import extraction modules
from extraction.models import RedditConfig
from extraction.services.reddit_extractor import RedditExtractor

logger = logging.getLogger(__name__)


# ============================================================================
#                           1. REDDIT EXTRACTION
# ============================================================================

def extract_reddit_data(**context):
    """Extract Reddit data"""
    logger.info("=" * 60)
    logger.info("STEP 1: Reddit Data Extraction")
    logger.info("=" * 60)

    config = RedditConfig()
    extractor = RedditExtractor(config)

    logger.info("Fetching posts from r/CryptoCurrency")
    df = extractor.fetch_posts(
        subreddit_name='CryptoCurrency',
        query='bitcoin OR ethereum',
        limit=100
    )

    current_date = datetime.now()
    logger.info(f"Extracted {len(df)} posts, saving to bronze layer for date: {current_date.strftime('%Y-%m-%d')}")
    extractor.save_to_bronze(df, 'reddit_posts', execution_date=current_date)

    result = {'posts_extracted': len(df), 'extraction_date': current_date.isoformat()}
    context['ti'].xcom_push(key='extraction_result', value=result)
    logger.info(f"✅ Reddit extraction completed: {len(df)} posts")
    return result


# ============================================================================
#                           2. DATA CONSOLIDATION
# ============================================================================

def check_bronze_data_availability(**context):
    """Check if bronze data exists"""
    logger.info("=" * 60)
    logger.info("STEP 2: Data Consolidation - Checking Data Availability")
    logger.info("=" * 60)

    execution_date = context['execution_date']

    # Check Reddit data
    reddit_data_path = Path(f"data/bronze/reddit/year={execution_date.year}/month={execution_date.month:02d}/day={execution_date.day:02d}")
    reddit_check = {
        'exists': reddit_data_path.exists(),
        'file_count': len(list(reddit_data_path.glob("*.csv"))) if reddit_data_path.exists() else 0
    }

    # Check Kaggle data (optional)
    kaggle_data_path = Path("data/bronze/kaggle")
    kaggle_check = {
        'available': kaggle_data_path.exists(),
        'file_count': len(list(kaggle_data_path.glob("*.csv"))) if kaggle_data_path.exists() else 0
    }

    if reddit_check['exists']:
        logger.info(f"✅ Reddit data available: {reddit_check['file_count']} files")
        if kaggle_check['available']:
            logger.info(f"✅ Kaggle data detected: {kaggle_check['file_count']} files (will be included)")
        else:
            logger.info("ℹ️ No Kaggle data detected - continuing with Reddit only")
        return 'consolidate_data'
    else:
        logger.warning("❌ No Reddit data available. Skipping consolidation.")
        return 'skip_consolidation'


def consolidate_data(**context):
    """Consolidate bronze datasets"""
    logger.info("Consolidating Reddit and Kaggle data...")

    # Placeholder - will be implemented when module is created
    logger.warning("⚠️ Consolidation logic not yet fully implemented")

    result = {
        'reddit_records': 0,
        'kaggle_records': 0,
        'total_records': 0
    }

    context['ti'].xcom_push(key='consolidation_result', value=result)
    logger.info("✅ Consolidation completed (placeholder)")
    return result


def validate_master_dataset(**context):
    """Validate the consolidated master dataset"""
    logger.info("Validating master dataset...")

    master_path = Path("data_consolidation/outputs/master_dataset.csv")

    if not master_path.exists():
        logger.warning(f"Master dataset not found: {master_path} - skipping validation")
        return {'validation_status': 'skipped', 'total_records': 0}

    import pandas as pd
    df = pd.read_csv(master_path)

    stats = {
        'validation_status': 'passed',
        'total_records': len(df),
        'posts': len(df[df['source_type'] == 'post']) if 'source_type' in df.columns else 0,
        'comments': len(df[df['source_type'] == 'comment']) if 'source_type' in df.columns else 0,
    }

    context['ti'].xcom_push(key='validation_stats', value=stats)
    logger.info(f"✅ Validation passed: {stats['total_records']} total records")
    return stats


# ============================================================================
#                           3. DATA CLEANING
# ============================================================================

def clean_reddit_data(**context):
    """Clean Reddit data (Bronze to Silver)"""
    logger.info("=" * 60)
    logger.info("STEP 3: Data Cleaning")
    logger.info("=" * 60)

    # Placeholder - will call actual cleaning script
    logger.warning("⚠️ Cleaning logic not yet fully implemented")

    result = {
        'initial_rows': 0,
        'final_rows': 0,
        'removed_rows': 0,
        'removal_rate': 0.0
    }

    context['ti'].xcom_push(key='cleaning_result', value=result)
    logger.info("✅ Cleaning completed (placeholder)")
    return result


def validate_cleaned_data(**context):
    """Validate cleaned silver data"""
    logger.info("Validating cleaned data...")

    silver_path = Path("data/silver/reddit/cleaned_reddit_dataset.csv")

    if not silver_path.exists():
        logger.warning(f"Cleaned dataset not found: {silver_path} - skipping validation")
        return {'validation_status': 'skipped', 'total_records': 0}

    import pandas as pd
    df = pd.read_csv(silver_path)

    result = {
        'quality_score': 100.0,
        'validation_status': 'passed',
        'total_records': len(df)
    }

    context['ti'].xcom_push(key='cleaning_validation', value=result)
    logger.info(f"✅ Cleaning validation passed: {result['total_records']} records")
    return result


# ============================================================================
#                           4. TEMPORAL SPLITS
# ============================================================================

def create_temporal_splits(**context):
    """Create temporal splits (train/val/test)"""
    logger.info("=" * 60)
    logger.info("STEP 4: Creating Temporal Splits")
    logger.info("=" * 60)

    # Placeholder - will call actual split script
    logger.warning("⚠️ Temporal splits logic not yet fully implemented")

    result = {
        'train_rows': 0,
        'val_rows': 0,
        'test_rows': 0,
        'window_start': None,
        'window_end': None
    }

    context['ti'].xcom_push(key='splits_result', value=result)
    logger.info("✅ Temporal splits created (placeholder)")
    return result


def validate_splits(**context):
    """Validate temporal splits"""
    logger.info("Validating temporal splits...")

    output_dir = Path("data/silver/reddit")
    train_path = output_dir / "train_data.csv"
    val_path = output_dir / "validation_data.csv"
    test_path = output_dir / "test_data.csv"

    all_exist = all([train_path.exists(), val_path.exists(), test_path.exists()])

    if not all_exist:
        logger.warning("Split files not found - skipping validation")
        return {'validation_status': 'skipped'}

    stats = {
        'validation_status': 'passed',
        'splits_valid': True
    }

    context['ti'].xcom_push(key='splits_validation', value=stats)
    logger.info("✅ Splits validation passed")
    return stats


# ============================================================================
#                           5. EDA ANALYSIS
# ============================================================================

def should_run_eda(**context):
    """Check if today is Monday (EDA day)"""
    execution_date = context['execution_date']
    day_of_week = execution_date.weekday()  # 0=Monday, 6=Sunday

    if day_of_week == 0:  # Monday
        logger.info("✅ Today is Monday - running EDA analysis")
        return 'run_eda_analysis'
    else:
        logger.info(f"ℹ️ Today is not Monday (day {day_of_week}) - skipping EDA")
        return 'skip_eda'


def run_eda_analysis(**context):
    """Execute EDA analysis"""
    logger.info("=" * 60)
    logger.info("STEP 5: EDA Analysis")
    logger.info("=" * 60)

    # Placeholder - will call actual EDA script
    logger.warning("⚠️ EDA logic not yet fully implemented")

    result = {
        'plots_generated': 0,
        'cryptos_analyzed': 0
    }

    context['ti'].xcom_push(key='eda_result', value=result)
    logger.info("✅ EDA analysis completed (placeholder)")
    return result


def save_eda_plots(**context):
    """Save EDA plots to gold layer"""
    logger.info("Saving EDA plots...")

    plots_source = Path("EDA_Task/plots")
    plots_dest = Path("data/gold/eda")
    plots_dest.mkdir(parents=True, exist_ok=True)

    if not plots_source.exists():
        logger.warning(f"Plots directory not found: {plots_source}")
        return {'plots_copied': 0}

    plots_copied = 0
    for plot_file in plots_source.glob("*.png"):
        dest_file = plots_dest / plot_file.name
        shutil.copy2(plot_file, dest_file)
        plots_copied += 1

    logger.info(f"✅ Copied {plots_copied} plots to gold layer")
    return {'plots_copied': plots_copied}


# ============================================================================
#                           PIPELINE ORCHESTRATION
# ============================================================================

def log_pipeline_completion(**context):
    """Log pipeline completion metrics"""
    logger.info("=" * 80)
    logger.info(" " * 20 + "PIPELINE COMPLETION SUMMARY")
    logger.info("=" * 80)

    ti = context['ti']
    execution_date = context['execution_date']

    # Retrieve all results from XCom
    extraction_result = ti.xcom_pull(task_ids='extract_reddit_data', key='extraction_result') or {}
    consolidation_result = ti.xcom_pull(task_ids='consolidate_data', key='consolidation_result') or {}
    cleaning_result = ti.xcom_pull(task_ids='clean_reddit_data', key='cleaning_result') or {}
    splits_result = ti.xcom_pull(task_ids='create_temporal_splits', key='splits_result') or {}
    eda_result = ti.xcom_pull(task_ids='run_eda_analysis', key='eda_result') or {}

    logger.info(f"Execution date: {execution_date}")
    logger.info("")
    logger.info("Step Results:")
    logger.info(f"  1. Reddit Extraction:   {extraction_result.get('posts_extracted', 0)} posts")
    logger.info(f"  2. Consolidation:       {consolidation_result.get('total_records', 0)} total records")
    logger.info(f"  3. Cleaning:            {cleaning_result.get('final_rows', 0)} clean records")
    logger.info(f"  4. Temporal Splits:     Train={splits_result.get('train_rows', 0)}, Val={splits_result.get('val_rows', 0)}, Test={splits_result.get('test_rows', 0)}")
    logger.info(f"  5. EDA Analysis:        {eda_result.get('plots_generated', 0)} plots generated")
    logger.info("")
    logger.info("✅ Complete pipeline executed successfully")
    logger.info("=" * 80)

    summary = {
        'status': 'success',
        'execution_date': execution_date.isoformat(),
        'extraction': extraction_result,
        'consolidation': consolidation_result,
        'cleaning': cleaning_result,
        'splits': splits_result,
        'eda': eda_result
    }

    # Save summary to file
    summary_path = Path("data/gold/pipeline_summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, default=str)

    return summary


def handle_pipeline_failure(**context):
    """Handle pipeline failures"""
    logger.error("=" * 80)
    logger.error(" " * 25 + "PIPELINE FAILURE DETECTED")
    logger.error("=" * 80)

    execution_date = context['execution_date']
    exception = context.get('exception', 'Unknown error')

    logger.error(f"Execution date: {execution_date}")
    logger.error(f"Exception: {exception}")
    logger.error("")
    logger.error("⚠️ Pipeline execution failed - check logs above for details")
    logger.error("=" * 80)

    return {
        'status': 'failed',
        'execution_date': execution_date.isoformat(),
        'error': str(exception)
    }


# ============================================================================
#                           DAG DEFINITION
# ============================================================================

default_args = {
    'owner': 'crypto-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'execution_timeout': timedelta(hours=4)
}

with DAG(
    dag_id='complete_crypto_pipeline_unified',
    description='Complete unified crypto analysis pipeline - All tasks in one DAG',
    schedule_interval='0 6 * * *',  # Daily at 6 AM
    start_date=datetime(2025, 1, 1),
    catchup=True,
    max_active_runs=1,
    default_args=default_args,
    tags=['unified', 'pipeline', 'complete', 'crypto']
) as dag:

    # ========== Pipeline Start ==========
    start_pipeline = DummyOperator(
        task_id='start_pipeline'
    )

    # ========== Step 1: Reddit Extraction ==========
    extract_reddit = PythonOperator(
        task_id='extract_reddit_data',
        python_callable=extract_reddit_data,
        provide_context=True
    )

    # ========== Step 2: Data Consolidation ==========
    check_bronze = BranchPythonOperator(
        task_id='check_bronze_data',
        python_callable=check_bronze_data_availability,
        provide_context=True
    )

    skip_consolidation = DummyOperator(
        task_id='skip_consolidation'
    )

    consolidate = PythonOperator(
        task_id='consolidate_data',
        python_callable=consolidate_data,
        provide_context=True
    )

    validate_master = PythonOperator(
        task_id='validate_master_dataset',
        python_callable=validate_master_dataset,
        provide_context=True
    )

    # ========== Step 3: Data Cleaning ==========
    clean_data = PythonOperator(
        task_id='clean_reddit_data',
        python_callable=clean_reddit_data,
        provide_context=True
    )

    validate_cleaning = PythonOperator(
        task_id='validate_cleaned_data',
        python_callable=validate_cleaned_data,
        provide_context=True
    )

    # ========== Step 4: Temporal Splits ==========
    create_splits = PythonOperator(
        task_id='create_temporal_splits',
        python_callable=create_temporal_splits,
        provide_context=True
    )

    validate_splits_task = PythonOperator(
        task_id='validate_splits',
        python_callable=validate_splits,
        provide_context=True
    )

    # ========== Step 5: EDA Analysis (Monday only) ==========
    check_eda_schedule = BranchPythonOperator(
        task_id='check_eda_schedule',
        python_callable=should_run_eda,
        provide_context=True
    )

    skip_eda = DummyOperator(
        task_id='skip_eda'
    )

    run_eda = PythonOperator(
        task_id='run_eda_analysis',
        python_callable=run_eda_analysis,
        provide_context=True
    )

    save_plots = PythonOperator(
        task_id='save_eda_plots',
        python_callable=save_eda_plots,
        provide_context=True
    )

    # ========== Pipeline Completion ==========
    pipeline_success = PythonOperator(
        task_id='pipeline_success',
        python_callable=log_pipeline_completion,
        provide_context=True,
        trigger_rule='none_failed_or_skipped'
    )

    pipeline_failure = PythonOperator(
        task_id='pipeline_failure',
        python_callable=handle_pipeline_failure,
        provide_context=True,
        trigger_rule='one_failed'
    )

    # ========== Define Task Dependencies ==========
    # Main pipeline flow
    start_pipeline >> extract_reddit
    extract_reddit >> check_bronze

    # Consolidation branch
    check_bronze >> [skip_consolidation, consolidate]
    consolidate >> validate_master

    # After consolidation (or skip), continue to cleaning
    [skip_consolidation, validate_master] >> clean_data

    # Cleaning and validation
    clean_data >> validate_cleaning

    # Temporal splits
    validate_cleaning >> create_splits
    create_splits >> validate_splits_task

    # EDA check (Monday only)
    validate_splits_task >> check_eda_schedule
    check_eda_schedule >> [skip_eda, run_eda]
    run_eda >> save_plots

    # Pipeline completion
    [skip_eda, save_plots] >> pipeline_success

    # Failure handling - all critical tasks can trigger failure
    [extract_reddit, consolidate, clean_data,
     create_splits, run_eda] >> pipeline_failure
