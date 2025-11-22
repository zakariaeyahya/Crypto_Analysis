"""
Data Consolidation Module
Consolidates Reddit and Kaggle data into unified master dataset
"""
import pandas as pd
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class DataConsolidator:
    """Consolidates data from multiple sources into unified schema"""
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize DataConsolidator
        
        Args:
            output_dir: Directory for output files
        """
        if output_dir is None:
            self.output_dir = Path(__file__).parent / "outputs"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.master_dataset_path = self.output_dir / "master_dataset.csv"
        
        logger.info(f"DataConsolidator initialized. Output: {self.output_dir}")
    
    def load_reddit_data(self, execution_date: datetime) -> pd.DataFrame:
        """
        Load Reddit data for execution date
        
        Args:
            execution_date: Date to load data for
            
        Returns:
            DataFrame with Reddit data
        """
        year = execution_date.strftime('%Y')
        month = execution_date.strftime('%m')
        day = execution_date.strftime('%d')
        
        reddit_path = Path(f"data/bronze/reddit/year={year}/month={month}/day={day}")
        
        dfs = []
        
        # Load posts
        posts_files = list(reddit_path.glob("reddit_posts_*.csv"))
        for file in posts_files:
            try:
                df = pd.read_csv(file)
                df['source_type'] = 'post'
                df['source_platform'] = 'reddit'
                dfs.append(df)
                logger.info(f"Loaded {len(df)} posts from {file.name}")
            except Exception as e:
                logger.warning(f"Failed to load {file}: {e}")
        
        # Load comments
        comments_files = list(reddit_path.glob("reddit_comments_*.csv"))
        for file in comments_files:
            try:
                df = pd.read_csv(file)
                df['source_type'] = 'comment'
                df['source_platform'] = 'reddit'
                dfs.append(df)
                logger.info(f"Loaded {len(df)} comments from {file.name}")
            except Exception as e:
                logger.warning(f"Failed to load {file}: {e}")
        
        if not dfs:
            logger.warning(f"No Reddit data found for {execution_date.strftime('%Y-%m-%d')}")
            return pd.DataFrame()
        
        combined = pd.concat(dfs, ignore_index=True)
        logger.info(f"Total Reddit records loaded: {len(combined)}")
        return combined
    
    def detect_and_load_kaggle_data(self) -> pd.DataFrame:
        """
        Detect and load Kaggle data if available (automatic detection)
        
        Returns:
            DataFrame with Kaggle data, empty if not available
        """
        kaggle_path = Path("data/bronze/kaggle")
        
        if not kaggle_path.exists():
            logger.info("Kaggle data directory does not exist - skipping Kaggle")
            return pd.DataFrame()
        
        # Look for any CSV files (not just bitcoin_tweets)
        csv_files = sorted(kaggle_path.glob("*.csv"), 
                          key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not csv_files:
            logger.info("No Kaggle CSV files found - continuing with Reddit only")
            return pd.DataFrame()
        
        # Use most recent file
        latest_file = csv_files[0]
        try:
            logger.info(f"Detected Kaggle data: {latest_file.name}")
            # Load all data (can be large, but necessary for consolidation)
            df = pd.read_csv(latest_file, nrows=None)
            df['source_type'] = 'tweet'
            df['source_platform'] = 'kaggle'
            logger.info(f"✅ Loaded {len(df)} Kaggle records from {latest_file.name}")
            return df
        except Exception as e:
            logger.error(f"Failed to load Kaggle data: {e}")
            logger.warning("Continuing with Reddit data only")
            return pd.DataFrame()
    
    def load_kaggle_data(self) -> pd.DataFrame:
        """
        Alias for detect_and_load_kaggle_data() for backward compatibility
        
        Returns:
            DataFrame with Kaggle data, empty if not available
        """
        return self.detect_and_load_kaggle_data()
    
    def standardize_reddit_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize Reddit data to unified schema
        
        Args:
            df: Reddit DataFrame
            
        Returns:
            Standardized DataFrame
        """
        if df.empty:
            return df
        
        standardized = pd.DataFrame()
        
        # unified_id
        if 'id' in df.columns:
            standardized['unified_id'] = df.apply(
                lambda row: f"p_reddit_{row['id']}" if row.get('source_type') == 'post' 
                else f"c_reddit_{row['id']}", axis=1
            )
        elif 'submission_id' in df.columns:
            standardized['unified_id'] = df.apply(
                lambda row: f"p_reddit_{row['submission_id']}" if row.get('source_type') == 'post'
                else f"c_reddit_{row.get('comment_id', row.get('id', 'unknown'))}", axis=1
            )
        else:
            logger.warning("No ID column found in Reddit data")
            standardized['unified_id'] = df.index.map(lambda x: f"reddit_{x}")
        
        # text_content
        if 'title' in df.columns and 'selftext' in df.columns:
            standardized['text_content'] = (df['title'].fillna('') + ' ' + 
                                           df['selftext'].fillna('')).str.strip()
        elif 'body' in df.columns:
            standardized['text_content'] = df['body'].fillna('')
        elif 'text' in df.columns:
            standardized['text_content'] = df['text'].fillna('')
        else:
            standardized['text_content'] = ''
            logger.warning("No text content column found in Reddit data")
        
        # created_date
        if 'created_utc' in df.columns:
            standardized['created_date'] = pd.to_datetime(df['created_utc'], unit='s', errors='coerce')
        elif 'created_date' in df.columns:
            standardized['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
        else:
            standardized['created_date'] = pd.NaT
            logger.warning("No date column found in Reddit data")
        
        # author
        standardized['author'] = df.get('author', df.get('author_name', 'unknown'))
        
        # source_type and source_platform
        standardized['source_type'] = df.get('source_type', 'unknown')
        standardized['source_platform'] = df.get('source_platform', 'reddit')
        
        # subreddit
        standardized['subreddit'] = df.get('subreddit', df.get('subreddit_name', ''))
        
        # score
        standardized['score'] = df.get('score', df.get('upvotes', 0))
        
        # crypto_mentions (extract from subreddit or text)
        standardized['crypto_mentions'] = standardized['subreddit'].fillna('')
        
        return standardized
    
    def standardize_kaggle_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize Kaggle data to unified schema
        
        Args:
            df: Kaggle DataFrame
            
        Returns:
            Standardized DataFrame
        """
        if df.empty:
            return df
        
        standardized = pd.DataFrame()
        
        # unified_id
        if 'id' in df.columns or 'tweet_id' in df.columns:
            id_col = 'id' if 'id' in df.columns else 'tweet_id'
            standardized['unified_id'] = df[id_col].apply(lambda x: f"tweet_kaggle_{x}")
        else:
            standardized['unified_id'] = df.index.map(lambda x: f"kaggle_{x}")
        
        # text_content
        if 'tweet' in df.columns:
            standardized['text_content'] = df['tweet'].fillna('')
        elif 'text' in df.columns:
            standardized['text_content'] = df['text'].fillna('')
        else:
            standardized['text_content'] = ''
        
        # created_date
        if 'timestamp' in df.columns:
            standardized['created_date'] = pd.to_datetime(df['timestamp'], errors='coerce')
        elif 'date' in df.columns:
            standardized['created_date'] = pd.to_datetime(df['date'], errors='coerce')
        else:
            standardized['created_date'] = pd.NaT
        
        # author (Kaggle might not have author)
        standardized['author'] = df.get('user', df.get('author', 'unknown'))
        
        # source_type and source_platform
        standardized['source_type'] = df.get('source_type', 'tweet')
        standardized['source_platform'] = df.get('source_platform', 'kaggle')
        
        # subreddit (not applicable for Kaggle, but keep for consistency)
        standardized['subreddit'] = 'bitcoin'  # Kaggle dataset is Bitcoin-focused
        
        # score (Kaggle might not have score)
        standardized['score'] = df.get('likes', df.get('score', 0))
        
        # crypto_mentions
        standardized['crypto_mentions'] = 'bitcoin'
        
        return standardized
    
    def merge_datasets(self, reddit_df: pd.DataFrame, kaggle_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge Reddit and Kaggle datasets
        
        Args:
            reddit_df: Standardized Reddit DataFrame
            kaggle_df: Standardized Kaggle DataFrame
            
        Returns:
            Merged DataFrame
        """
        dfs = []
        
        if not reddit_df.empty:
            dfs.append(reddit_df)
        
        if not kaggle_df.empty:
            dfs.append(kaggle_df)
        
        if not dfs:
            logger.warning("No data to merge")
            return pd.DataFrame()
        
        merged = pd.concat(dfs, ignore_index=True)
        
        # Remove duplicates based on unified_id
        before_dedup = len(merged)
        merged = merged.drop_duplicates(subset=['unified_id'], keep='first')
        after_dedup = len(merged)
        
        if before_dedup != after_dedup:
            logger.info(f"Removed {before_dedup - after_dedup} duplicate records")
        
        return merged
    
    def save_master_dataset(self, df: pd.DataFrame, append: bool = True) -> Path:
        """
        Save master dataset
        
        Args:
            df: DataFrame to save
            append: If True, append to existing file; if False, overwrite
            
        Returns:
            Path to saved file
        """
        if df.empty:
            logger.warning("No data to save")
            return self.master_dataset_path
        
        if append and self.master_dataset_path.exists():
            # Load existing data
            existing_df = pd.read_csv(self.master_dataset_path)
            logger.info(f"Loading existing master dataset: {len(existing_df)} records")
            
            # Combine
            combined = pd.concat([existing_df, df], ignore_index=True)
            
            # Remove duplicates
            before_dedup = len(combined)
            combined = combined.drop_duplicates(subset=['unified_id'], keep='first')
            after_dedup = len(combined)
            
            if before_dedup != after_dedup:
                logger.info(f"Removed {before_dedup - after_dedup} duplicates during append")
            
            df = combined
        
        # Save
        df.to_csv(self.master_dataset_path, index=False)
        logger.info(f"Saved master dataset: {len(df)} records to {self.master_dataset_path}")
        
        return self.master_dataset_path


def consolidate_bronze_datasets(execution_date: datetime, append: bool = True) -> Dict[str, Any]:
    """
    Main function to consolidate bronze datasets
    
    Args:
        execution_date: Date to consolidate data for
        append: Whether to append to existing master dataset
        
    Returns:
        Dictionary with consolidation results
    """
    logger.info("=" * 60)
    logger.info("Starting data consolidation")
    logger.info("=" * 60)
    
    consolidator = DataConsolidator()
    
    # Load Reddit data
    reddit_df = consolidator.load_reddit_data(execution_date)
    reddit_count = len(reddit_df)
    
    # Detect and load Kaggle data (automatic detection)
    kaggle_df = consolidator.detect_and_load_kaggle_data()
    kaggle_count = len(kaggle_df)
    
    if kaggle_count > 0:
        logger.info(f"✅ Kaggle data automatically detected and included: {kaggle_count} records")
    else:
        logger.info("ℹ️ No Kaggle data detected - continuing with Reddit only")
    
    # Standardize schemas
    if not reddit_df.empty:
        reddit_df = consolidator.standardize_reddit_schema(reddit_df)
    
    if not kaggle_df.empty:
        kaggle_df = consolidator.standardize_kaggle_schema(kaggle_df)
    
    # Merge
    merged_df = consolidator.merge_datasets(reddit_df, kaggle_df)
    
    # Save
    if not merged_df.empty:
        consolidator.save_master_dataset(merged_df, append=append)
    
    result = {
        'records_consolidated': len(merged_df),
        'reddit_records': reddit_count,
        'kaggle_records': kaggle_count,
        'master_dataset_path': str(consolidator.master_dataset_path)
    }
    
    logger.info("=" * 60)
    logger.info("Consolidation completed")
    logger.info(f"Reddit records: {reddit_count}")
    logger.info(f"Kaggle records: {kaggle_count}")
    logger.info(f"Total consolidated: {len(merged_df)}")
    logger.info("=" * 60)
    
    return result


