"""
Complete Crypto Sentiment Analysis Pipeline DAG
================================================
Complete pipeline for Reddit crypto data extraction, cleaning and sentiment analysis.

Medallion Architecture:
- Bronze: Reddit extraction (data/bronze/reddit/) - partitioned by date
- Silver: Consolidated data cleaning (data/silver/reddit/cleaned_reddit_dataset.csv)
- Silver: Sentiment analysis (data/silver/reddit/sentiment_analysis_YYYYMMDD.csv)
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
from pathlib import Path
import pandas as pd
import logging
import json
import importlib.util

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

default_args = {
    'owner': 'crypto_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
}

dag = DAG(
    'complete_crypto_pipeline_unified',
    default_args=default_args,
    description='Complete pipeline: Reddit Extraction → Consolidated Data Cleaning → Sentiment Analysis',
    schedule_interval=timedelta(days=1),  # Daily execution
    catchup=True,  # ENABLED: Automatically recover missed days
    max_active_runs=1,  # Limit to 1 execution at a time to avoid overload
    tags=['crypto', 'reddit', 'sentiment', 'nlp', 'unified'],
)


def extract_reddit_data(**context):
    """
    Step 1: Reddit data extraction
    Output: data/bronze/reddit/year=YYYY/month=MM/day=DD/
    """
    import logging
    import pandas as pd
    from extraction.services.reddit_extractor import RedditExtractor
    from extraction.models.config import RedditConfig
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("STEP 1: REDDIT EXTRACTION (BRONZE LAYER)")
    logger.info("=" * 80)
    
    try:
        # Get execution date from context
        execution_date = context.get('execution_date')
        if execution_date is None:
            from datetime import datetime
            execution_date = datetime.now()
        else:
            # Convert pendulum datetime to standard datetime if needed
            if hasattr(execution_date, 'to_datetime_string'):
                execution_date = execution_date.to_datetime_string()
            if isinstance(execution_date, str):
                execution_date = datetime.fromisoformat(execution_date.replace('Z', '+00:00'))
            elif hasattr(execution_date, 'year'):
                execution_date = datetime(
                    execution_date.year,
                    execution_date.month,
                    execution_date.day,
                    execution_date.hour,
                    execution_date.minute,
                    execution_date.second
                )
        
        logger.info(f"Execution date: {execution_date}")
        
        # Initialize extractor
        config = RedditConfig()
        extractor = RedditExtractor(config)
        
        # Increase limit to retrieve more posts (wider window)
        # This allows retrieving posts from previous days if DAG didn't run
        posts_limit = max(config.max_posts, 500)  # Minimum 500 posts to cover multiple days
        
        logger.info("Extracting Reddit posts...")
        logger.info(f"Posts limit: {posts_limit} (to cover missed days)")
        
        # Fetch posts
        _ = extractor.fetch_posts(
            subreddit_name=config.subreddit,
            query=config.query,
            limit=posts_limit,  # Increased limit
            sort="new"
        )
        
        # Get extracted data
        posts_df = getattr(extractor, "_last_posts_df", pd.DataFrame())
        comments_df = getattr(extractor, "_last_comments_df", pd.DataFrame())
        
        # Save to bronze layer with execution date
        if not posts_df.empty:
            extractor.save_posts_to_bronze(
                posts_df, 
                base_filename='reddit_posts',
                execution_date=execution_date
            )
            logger.info(f"Saved {len(posts_df)} posts to bronze layer")
        else:
            logger.warning("No Reddit posts extracted")
        
        if not comments_df.empty:
            extractor.save_comments_to_bronze(
                comments_df, 
                base_filename='reddit_comments',
                execution_date=execution_date
            )
            logger.info(f"Saved {len(comments_df)} comments to bronze layer")
        else:
            logger.warning("No Reddit comments extracted")
        
        logger.info("Reddit extraction completed successfully")
        return {
            'posts_count': len(posts_df),
            'comments_count': len(comments_df),
            'execution_date': execution_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error during Reddit extraction: {str(e)}")
        raise


def clean_reddit_data(**context):
    """
    Step 2: Reddit data cleaning - CONSOLIDATION OF ALL DATA
    Input: data/bronze/reddit/ (ALL scraped data from all days)
    Output: data/silver/reddit/cleaned_reddit_dataset.csv (consolidated cleaned file)
    """
    import logging
    import sys
    import importlib.util
    import pandas as pd
    from pathlib import Path
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("STEP 2: DATA CLEANING - CONSOLIDATION OF ALL DATA (SILVER LAYER)")
    logger.info("=" * 80)
    
    try:
        project_root = Path(__file__).parent.parent.parent
        bronze_dir = project_root / "data" / "bronze" / "reddit"
        silver_dir = project_root / "data" / "silver" / "reddit"
        silver_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Loading ALL bronze data (all days)...")
        
        # Load ALL bronze data from all dates
        all_dataframes = []
        
        # Iterate through all year/month/day partitions
        for year_dir in bronze_dir.glob("year=*"):
            year = year_dir.name.split("=")[1]
            for month_dir in year_dir.glob("month=*"):
                month = month_dir.name.split("=")[1]
                for day_dir in month_dir.glob("day=*"):
                    day = day_dir.name.split("=")[1]
                    
                    # Find all CSV files in this partition
                    csv_files = list(day_dir.glob("*.csv"))
                    for csv_file in csv_files:
                        if "summary" not in csv_file.name:  # Skip summary files
                            try:
                                df = pd.read_csv(csv_file)
                                if not df.empty:
                                    # Add partition info
                                    df['bronze_year'] = year
                                    df['bronze_month'] = month
                                    df['bronze_day'] = day
                                    df['bronze_source_file'] = csv_file.name
                                    all_dataframes.append(df)
                                    logger.info(f"  Loaded: {csv_file} ({len(df)} rows)")
                            except Exception as e:
                                logger.warning(f"  Error loading {csv_file}: {e}")
        
        if not all_dataframes:
            logger.warning("No bronze data found!")
            return {
                'initial_rows': 0,
                'final_rows': 0,
                'removed_rows': 0,
                'removal_rate': 0.0
            }

        # Consolidate all dataframes
        logger.info(f"Consolidating {len(all_dataframes)} files...")
        df_consolidated = pd.concat(all_dataframes, ignore_index=True)
        logger.info(f"Consolidated data: {len(df_consolidated)} total rows")
        
        # Load cleaning script
        cleaning_script = project_root / "data_cleaning" / "Script" / "Reddit-Dataset-Cleaning.py"
        
        if not cleaning_script.exists():
            raise FileNotFoundError(f"Cleaning script not found: {cleaning_script}")
        
        # Load module dynamically
        spec = importlib.util.spec_from_file_location("reddit_cleaning", cleaning_script)
        cleaning_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cleaning_module)
        
        # Load checkpoint
        checkpoint_file = silver_dir / "checkpoint.json"
        processed_ids = set()
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
                processed_ids = set(checkpoint.get('processed_ids', []))
            logger.info(f"Checkpoint loaded: {len(processed_ids)} IDs already processed")
        
        # Filter out already processed IDs
        id_column = None
        for col in ['submission_id', 'id', 'unified_id']:
            if col in df_consolidated.columns:
                id_column = col
                break
        
        if id_column:
            initial_count = len(df_consolidated)
            df_consolidated = df_consolidated[~df_consolidated[id_column].isin(processed_ids)]
            new_count = len(df_consolidated)
            logger.info(f"  {initial_count - new_count} rows already processed (checkpoint)")
        
        # Apply cleaning transformations
        logger.info("Cleaning in progress...")
        
        # Remove duplicates
        before_dedup = len(df_consolidated)
        if id_column:
            df_consolidated = df_consolidated.drop_duplicates(subset=[id_column], keep='first')
        else:
            df_consolidated = df_consolidated.drop_duplicates()
        after_dedup = len(df_consolidated)
        
        logger.info(f"  Removed {before_dedup - after_dedup} duplicates")
        
        # Save cleaned consolidated data
        output_file = silver_dir / "cleaned_reddit_dataset.csv"
        df_consolidated.to_csv(output_file, index=False)
        logger.info(f"Consolidated cleaned data saved: {output_file}")
        logger.info(f"  Total: {len(df_consolidated)} rows")
        
        # Update checkpoint
        if id_column:
            new_ids = set(df_consolidated[id_column].dropna().astype(str))
            processed_ids.update(new_ids)
            checkpoint_data = {
                'processed_ids': list(processed_ids),
                'last_run': datetime.now().isoformat(),
                'total_processed': len(processed_ids)
            }
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Checkpoint updated: {len(processed_ids)} total IDs")
        
        result = {
            'initial_rows': before_dedup,
            'final_rows': len(df_consolidated),
            'removed_rows': before_dedup - len(df_consolidated),
            'removal_rate': (before_dedup - len(df_consolidated)) / before_dedup if before_dedup > 0 else 0.0,
            'output_file': str(output_file)
        }
        
        logger.info(f"Cleaning completed: {result['final_rows']} final rows")
        logger.info(f"  Initial rows: {result['initial_rows']}")
        logger.info(f"  Removed rows: {result['removed_rows']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during cleaning: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise


def analyze_sentiment(**context):
    """
    Step 3: Sentiment analysis with fine-tuned model
    Input: data/silver/reddit/cleaned_reddit_dataset.csv (consolidated file from all days)
    Output: data/silver/reddit/sentiment_analysis_YYYYMMDD.csv (in SILVER, not GOLD)
    """
    import logging
    import pandas as pd
    from pathlib import Path
    from datetime import datetime
    import sys
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("STEP 3: SENTIMENT ANALYSIS (SILVER LAYER)")
    logger.info("=" * 80)

    try:
        # Get execution date
        execution_date = context.get('execution_date')
        if execution_date is None:
            execution_date = datetime.now()
        else:
            if hasattr(execution_date, 'to_datetime_string'):
                execution_date = execution_date.to_datetime_string()
            if isinstance(execution_date, str):
                execution_date = datetime.fromisoformat(execution_date.replace('Z', '+00:00'))
            elif hasattr(execution_date, 'year'):
                execution_date = datetime(
                    execution_date.year,
                    execution_date.month,
                    execution_date.day,
                    execution_date.hour,
                    execution_date.minute,
                    execution_date.second
                )
        
        # Paths - OUTPUT IN SILVER, NOT GOLD
        project_root = Path(__file__).parent.parent.parent
        silver_path = project_root / "data" / "silver" / "reddit" / "cleaned_reddit_dataset.csv"
        silver_dir = project_root / "data" / "silver" / "reddit"
        silver_dir.mkdir(parents=True, exist_ok=True)
        
        # Output file with date - IN SILVER
        date_str = execution_date.strftime('%Y%m%d')
        output_file = silver_dir / f"sentiment_analysis_{date_str}.csv"
        
        logger.info(f"Execution date: {execution_date}")
        logger.info(f"Reading from: {silver_path}")
        logger.info(f"Saving to: {output_file}")
        
        # Load cleaned data
        if not silver_path.exists():
            logger.warning(f"Silver file not found: {silver_path}")
            return {'status': 'skipped', 'reason': 'no_silver_data'}
        
        logger.info("Loading cleaned data...")
        df = pd.read_csv(silver_path)
        logger.info(f"Loaded {len(df)} rows")
        
        if df.empty:
            logger.warning("No data to analyze")
            return {'status': 'skipped', 'reason': 'empty_data'}
        
        # Import sentiment predictor
        finetuning_path = project_root / "Finetuning"
        sys.path.insert(0, str(finetuning_path))
        
        from inference import SentimentPredictor
        
        # Initialize predictor
        model_path = finetuning_path / "output" / "models" / "best_model"
        if not model_path.exists():
            # Try alternative path
            model_path = finetuning_path / "models" / "best_model"
        
        logger.info(f"Loading model from: {model_path}")
        predictor = SentimentPredictor(model_path=str(model_path), use_cuda=False)
        logger.info("Model loaded")
        
        # Prepare text column (combine title and text/body if available)
        text_columns = []
        if 'title' in df.columns:
            text_columns.append('title')
        if 'text' in df.columns:
            text_columns.append('text')
        elif 'body' in df.columns:
            text_columns.append('body')
        
        if not text_columns:
            logger.error("No text column found (title, text, body)")
            raise ValueError("No text column available for analysis")
        
        # Combine text columns
        if len(text_columns) > 1:
            df['combined_text'] = df[text_columns].fillna('').agg(' '.join, axis=1)
        else:
            df['combined_text'] = df[text_columns[0]].fillna('')
        
        # Remove empty texts
        df = df[df['combined_text'].str.strip().str.len() > 0].copy()
        logger.info(f"{len(df)} rows with valid text")
        
        # Analyze sentiment in batches
        logger.info("Sentiment analysis in progress...")
        texts = df['combined_text'].tolist()
        batch_size = 32
        
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = predictor.predict_batch(batch, batch_size=batch_size)
            results.extend(batch_results)
            
            if (i + batch_size) % 100 == 0:
                logger.info(f"  Processed {min(i + batch_size, len(texts))}/{len(texts)} rows...")
        
        logger.info(f"Analysis completed for {len(results)} texts")
        
        # Add sentiment columns to dataframe
        df['sentiment'] = [r['label'] for r in results]
        df['sentiment_confidence'] = [r['confidence'] for r in results]
        
        # Save to silver layer
        df.to_csv(output_file, index=False)
        logger.info(f"Results saved: {output_file}")
        logger.info(f"  Total: {len(df)} rows")
        logger.info(f"  Positive: {len(df[df['sentiment'] == 'positive'])}")
        logger.info(f"  Negative: {len(df[df['sentiment'] == 'negative'])}")
        
        return {
            'status': 'success',
            'total_rows': len(df),
            'positive_count': len(df[df['sentiment'] == 'positive']),
            'negative_count': len(df[df['sentiment'] == 'negative']),
            'output_file': str(output_file)
        }
        
    except Exception as e:
        logger.error(f"Error during sentiment analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise


# Define tasks
extract_task = PythonOperator(
    task_id='extract_reddit',
    python_callable=extract_reddit_data,
    dag=dag,
)

clean_task = PythonOperator(
    task_id='clean_data',
    python_callable=clean_reddit_data,
    dag=dag,
)

sentiment_task = PythonOperator(
    task_id='analyze_sentiment',
    python_callable=analyze_sentiment,
    dag=dag,
)

# Define task dependencies: extraction → cleaning → sentiment
extract_task >> clean_task >> sentiment_task
