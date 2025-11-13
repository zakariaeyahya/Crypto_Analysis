from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pathlib import Path
import yaml

from extraction.models import RedditConfig
from extraction.services.reddit_extractor import RedditExtractor


def extract_reddit_data(**context):
    config = RedditConfig()
    extractor = RedditExtractor(config)

    df = extractor.fetch_posts(
        subreddit_name='CryptoCurrency',
        query='bitcoin OR ethereum',
        limit=100
    )

    extractor.save_to_bronze(df, 'reddit_posts', execution_date=context['execution_date'])
    return {'posts_extracted': len(df)}


config_path = Path(__file__).parent / 'config' / 'dag_config.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

reddit_config = config['reddit_extraction']
default_args = config['default_args']
default_args['retry_delay'] = timedelta(minutes=default_args.pop('retry_delay_minutes'))

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
