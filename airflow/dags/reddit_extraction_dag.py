from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import logging

from extraction.models import RedditConfig
from extraction.services.reddit_extractor import RedditExtractor

# Configure logger
logger = logging.getLogger(__name__)


def extract_reddit_data(**context):
    logger.info("Starting Reddit data extraction")
    config = RedditConfig()
    extractor = RedditExtractor(config)

    logger.info("Fetching posts from r/CryptoCurrency")
    df = extractor.fetch_posts(
        subreddit_name='CryptoCurrency',
        query='bitcoin OR ethereum',
        limit=100
    )

    # Use current date for storage, not execution_date (which is for scheduling)
    # This ensures data is always saved with today's date regardless of when DAG runs
    current_date = datetime.now()
    logger.info(f"Extracted {len(df)} posts, saving to bronze layer for date: {current_date.strftime('%Y-%m-%d')}")
    extractor.save_to_bronze(df, 'reddit_posts', execution_date=current_date)
    logger.info("Reddit data extraction completed successfully")
    return {'posts_extracted': len(df)}


# Load and validate YAML configuration
config_path = Path(__file__).parent / 'config' / 'dag_config.yaml'

try:
    if not config_path.exists():
        error_msg = f"Configuration file does not exist: {config_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if config is None:
        error_msg = "YAML file is empty or invalid"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if 'reddit_extraction' not in config:
        error_msg = "Missing 'reddit_extraction' key in configuration file"
        logger.error(error_msg)
        raise KeyError(error_msg)
    
    if 'default_args' not in config:
        error_msg = "Missing 'default_args' key in configuration file"
        logger.error(error_msg)
        raise KeyError(error_msg)
    
    reddit_config = config['reddit_extraction']
    default_args = config['default_args'].copy()
    
    # Convert retry_delay_minutes to retry_delay (timedelta)
    if 'retry_delay_minutes' in default_args:
        default_args['retry_delay'] = timedelta(minutes=default_args.pop('retry_delay_minutes'))
    
    # Convert execution_timeout_minutes to execution_timeout (timedelta)
    if 'execution_timeout_minutes' in default_args:
        default_args['execution_timeout'] = timedelta(minutes=default_args.pop('execution_timeout_minutes'))
    
    logger.info(f"Successfully loaded configuration from {config_path}")
    
except FileNotFoundError as e:
    logger.error(f"ERROR: {e}")
    raise
except yaml.YAMLError as e:
    error_msg = f"YAML parsing error in {config_path}: {e}"
    logger.error(error_msg)
    raise ValueError(error_msg) from e
except (KeyError, ValueError) as e:
    error_msg = f"Invalid configuration: {e}"
    logger.error(error_msg)
    raise
except Exception as e:
    error_msg = f"Unexpected error while loading configuration: {e}"
    logger.error(error_msg)
    raise

with DAG(
    dag_id=reddit_config['dag_id'],
    description=reddit_config['description'],
    schedule_interval=reddit_config['schedule_interval'],
    start_date=datetime.strptime(reddit_config['start_date'], '%Y-%m-%d'),
    catchup=reddit_config['catchup'],
    max_active_runs=reddit_config['max_active_runs'],
    default_args=default_args,
    tags=['reddit', 'crypto', 'extraction']
) as dag:

    extract_task = PythonOperator(
        task_id=reddit_config['task_id'],
        python_callable=extract_reddit_data,
        provide_context=True
    )
