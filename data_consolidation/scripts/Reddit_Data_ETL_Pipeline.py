import pandas as pd
import numpy as np
from datetime import datetime
import re
import logging
import glob
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedditDataETL:
    """
    ETL Pipeline for consolidating Reddit posts and comments data
    into a unified master dataset for sentiment analysis.
    Automatically detects file schemas based on filename patterns.
    """
    
    def __init__(self, data_directory='.'):
        """
        Initialize the ETL pipeline with a directory path.
        
        Args:
            data_directory: Directory containing all the CSV files
        """
        self.data_directory = data_directory
        self.master_df = None
        
        # Get all CSV files in the directory
        all_csv_files = glob.glob(os.path.join(data_directory, '*.csv'))
        
        # Categorize files based on naming patterns
        self.schema_a_files = []  # crypto_posts
        self.schema_b_files = []  # reddit_posts
        self.schema_c_files = []  # crypto_comments
        self.unrecognized_files = []
        
        for file_path in all_csv_files:
            filename = os.path.basename(file_path).lower()
            
            if filename.startswith('crypto_posts'):
                self.schema_a_files.append(file_path)
            elif filename.startswith('reddit_posts'):
                self.schema_b_files.append(file_path)
            elif filename.startswith('crypto_comments'):
                self.schema_c_files.append(file_path)
            else:
                self.unrecognized_files.append(file_path)
        
        # Sort files for consistent processing order
        self.schema_a_files.sort()
        self.schema_b_files.sort()
        self.schema_c_files.sort()
        
        # Log discovery results
        logger.info("=" * 60)
        logger.info("FILE DISCOVERY")
        logger.info("=" * 60)
        logger.info(f"Directory: {os.path.abspath(data_directory)}")
        logger.info(f"Total CSV files found: {len(all_csv_files)}")
        logger.info(f"\nSchema A files (crypto_posts): {len(self.schema_a_files)}")
        for f in self.schema_a_files:
            logger.info(f"  - {os.path.basename(f)}")
        
        logger.info(f"\nSchema B files (reddit_posts): {len(self.schema_b_files)}")
        for f in self.schema_b_files:
            logger.info(f"  - {os.path.basename(f)}")
        
        logger.info(f"\nSchema C files (crypto_comments): {len(self.schema_c_files)}")
        for f in self.schema_c_files:
            logger.info(f"  - {os.path.basename(f)}")
        
        if self.unrecognized_files:
            logger.warning(f"\nUnrecognized files (will be skipped): {len(self.unrecognized_files)}")
            for f in self.unrecognized_files:
                logger.warning(f"  - {os.path.basename(f)}")
        
        logger.info("=" * 60)
        
        if not self.schema_a_files and not self.schema_b_files and not self.schema_c_files:
            raise ValueError(
                f"No matching CSV files found in directory: {data_directory}\n"
                f"Looking for files starting with: 'crypto_posts', 'reddit_posts', or 'crypto_comments'"
            )
        
    def standardize_datetime(self, date_value):
        """
        Convert various datetime formats to ISO 8601 format.
        
        Args:
            date_value: Can be string (ISO format), Unix timestamp (float/int), or None
            
        Returns:
            Standardized datetime string in ISO 8601 format
        """
        if pd.isna(date_value):
            return None
            
        try:
            # If it's already a string in ISO format
            if isinstance(date_value, str):
                # Try to parse it
                dt = pd.to_datetime(date_value)
                return dt.strftime('%Y-%m-%dT%H:%M:%S')
            
            # If it's a numeric Unix timestamp
            elif isinstance(date_value, (int, float)):
                dt = pd.to_datetime(date_value, unit='s')
                return dt.strftime('%Y-%m-%dT%H:%M:%S')
            
            # If it's already a datetime object
            elif isinstance(date_value, datetime):
                return date_value.strftime('%Y-%m-%dT%H:%M:%S')
            
        except Exception as e:
            logger.warning(f"Could not parse date: {date_value}. Error: {e}")
            return None
    
    def process_schema_a_posts(self, file_paths):
        """
        Process multiple files with Schema A (Posts - crypto_posts).
        Schema: subreddit,post_id,title,author,created_utc,score,upvote_ratio,num_comments,...
        
        Args:
            file_paths: List of file paths to process
        
        Returns:
            DataFrame with target schema
        """
        if not file_paths:
            return pd.DataFrame()
            
        logger.info(f"\nProcessing {len(file_paths)} Schema A files (crypto_posts)...")
        
        all_dataframes = []
        
        for file_path in file_paths:
            try:
                logger.info(f"  Reading: {os.path.basename(file_path)}")
                
                # Read the CSV with robust parsing
                df = pd.read_csv(
                    file_path,
                    dtype=str,
                    na_values=['', 'None', 'nan', 'NaN'],
                    keep_default_na=True
                )
                
                logger.info(f"    Loaded {len(df)} rows")
                
                # Create the transformed dataframe
                transformed = pd.DataFrame()
                
                # Map unified_id (prefix with p_)
                transformed['unified_id'] = 'p_' + df['post_id'].astype(str)
                
                # Combine title and selftext into text_content
                title = df['title'].fillna('')
                selftext = df['selftext'].fillna('')
                transformed['text_content'] = title + '\n\n' + selftext
                transformed['text_content'] = transformed['text_content'].str.strip()
                
                # Map other fields
                transformed['created_date'] = df['created_utc']
                transformed['author'] = df['author']
                transformed['source_type'] = 'post'
                transformed['subreddit'] = df['subreddit']
                transformed['source_platform'] = 'Reddit'
                transformed['crypto_mentions'] = None
                
                all_dataframes.append(transformed)
                logger.info(f"    Processed {len(transformed)} rows")
                
            except Exception as e:
                logger.error(f"  Error processing {file_path}: {e}")
                continue
        
        if all_dataframes:
            combined = pd.concat(all_dataframes, ignore_index=True)
            logger.info(f"Total rows from Schema A files: {len(combined)}")
            return combined
        else:
            logger.warning("No data processed from Schema A files")
            return pd.DataFrame()
    
    def process_schema_b_submissions(self, file_paths):
        """
        Process multiple files with Schema B (Submissions - reddit_posts).
        Schema: submission_id,title,text,score,num_comments,upvote_ratio,url,created_utc,...
        
        Args:
            file_paths: List of file paths to process
        
        Returns:
            DataFrame with target schema
        """
        if not file_paths:
            return pd.DataFrame()
            
        logger.info(f"\nProcessing {len(file_paths)} Schema B files (reddit_posts)...")
        
        all_dataframes = []
        
        for file_path in file_paths:
            try:
                logger.info(f"  Reading: {os.path.basename(file_path)}")
                
                # Read the CSV with robust parsing
                df = pd.read_csv(
                    file_path,
                    dtype=str,
                    na_values=['', 'None', 'nan', 'NaN'],
                    keep_default_na=True
                )
                
                logger.info(f"    Loaded {len(df)} rows")
                
                # Create the transformed dataframe
                transformed = pd.DataFrame()
                
                # Map unified_id (prefix with p_)
                transformed['unified_id'] = 'p_' + df['submission_id'].astype(str)
                
                # Combine title and text into text_content
                title = df['title'].fillna('')
                text = df['text'].fillna('')
                transformed['text_content'] = title + '\n\n' + text
                transformed['text_content'] = transformed['text_content'].str.strip()
                
                # Map created_utc (numeric timestamp)
                transformed['created_date'] = pd.to_numeric(df['created_utc'], errors='coerce')
                
                # Map other fields
                transformed['author'] = df['author']
                transformed['source_type'] = 'post'
                transformed['subreddit'] = df['subreddit']
                transformed['source_platform'] = 'Reddit'
                transformed['crypto_mentions'] = None
                
                all_dataframes.append(transformed)
                logger.info(f"    Processed {len(transformed)} rows")
                
            except Exception as e:
                logger.error(f"  Error processing {file_path}: {e}")
                continue
        
        if all_dataframes:
            combined = pd.concat(all_dataframes, ignore_index=True)
            logger.info(f"Total rows from Schema B files: {len(combined)}")
            return combined
        else:
            logger.warning("No data processed from Schema B files")
            return pd.DataFrame()
    
    def process_schema_c_comments(self, file_paths):
        """
        Process multiple files with Schema C (Comments - crypto_comments).
        Schema: post_id,subreddit,comment_id,author,created_utc,body,score,...
        
        Args:
            file_paths: List of file paths to process
        
        Returns:
            DataFrame with target schema
        """
        if not file_paths:
            return pd.DataFrame()
            
        logger.info(f"\nProcessing {len(file_paths)} Schema C files (crypto_comments)...")
        
        all_dataframes = []
        
        for file_path in file_paths:
            try:
                logger.info(f"  Reading: {os.path.basename(file_path)}")
                
                # Read the CSV with robust parsing
                df = pd.read_csv(
                    file_path,
                    dtype=str,
                    na_values=['', 'None', 'nan', 'NaN'],
                    keep_default_na=True
                )
                
                logger.info(f"    Loaded {len(df)} rows")
                
                # Create the transformed dataframe
                transformed = pd.DataFrame()
                
                # Map unified_id (prefix with c_)
                transformed['unified_id'] = 'c_' + df['comment_id'].astype(str)
                
                # Map body to text_content
                transformed['text_content'] = df['body'].fillna('')
                
                # Map other fields
                transformed['created_date'] = df['created_utc']
                transformed['author'] = df['author']
                transformed['source_type'] = 'comment'
                transformed['subreddit'] = df['subreddit']
                transformed['source_platform'] = 'Reddit'
                transformed['crypto_mentions'] = None
                
                all_dataframes.append(transformed)
                logger.info(f"    Processed {len(transformed)} rows")
                
            except Exception as e:
                logger.error(f"  Error processing {file_path}: {e}")
                continue
        
        if all_dataframes:
            combined = pd.concat(all_dataframes, ignore_index=True)
            logger.info(f"Total rows from Schema C files: {len(combined)}")
            return combined
        else:
            logger.warning("No data processed from Schema C files")
            return pd.DataFrame()
    
    def consolidate_and_clean(self, dataframes_list):
        """
        Consolidate multiple dataframes and perform cleaning operations.
        
        Args:
            dataframes_list: List of processed dataframes
            
        Returns:
            Cleaned and consolidated dataframe
        """
        logger.info("\n" + "=" * 60)
        logger.info("CONSOLIDATION & CLEANING")
        logger.info("=" * 60)
        
        # Filter out empty dataframes
        valid_dataframes = [df for df in dataframes_list if not df.empty]
        
        if not valid_dataframes:
            raise ValueError("No valid data to consolidate")
        
        # Concatenate all dataframes
        consolidated = pd.concat(valid_dataframes, ignore_index=True)
        logger.info(f"Total rows after concatenation: {len(consolidated):,}")
        
        # Standardize all dates
        logger.info("Standardizing datetime values...")
        consolidated['created_date'] = consolidated['created_date'].apply(self.standardize_datetime)
        
        # Remove rows with empty text content
        logger.info("Removing rows with empty text content...")
        before_count = len(consolidated)
        consolidated = consolidated[consolidated['text_content'].str.strip() != '']
        after_count = len(consolidated)
        logger.info(f"Removed {before_count - after_count:,} rows with empty text")
        
        # Deduplicate based on text_content
        logger.info("Deduplicating based on text_content...")
        before_count = len(consolidated)
        consolidated = consolidated.drop_duplicates(subset=['text_content'], keep='first')
        after_count = len(consolidated)
        logger.info(f"Removed {before_count - after_count:,} duplicate rows")
        
        # Reset index
        consolidated = consolidated.reset_index(drop=True)
        
        # Ensure column order matches target schema
        consolidated = consolidated[[
            'unified_id',
            'text_content',
            'created_date',
            'author',
            'source_type',
            'subreddit',
            'crypto_mentions',
            'source_platform'
        ]]
        
        logger.info(f"Final dataset size: {len(consolidated):,} rows")
        
        return consolidated
    
    def run_etl(self, output_path='master_dataset.csv'):
        """
        Execute the full ETL pipeline.
        
        Args:
            output_path: Path where the master dataset will be saved
            
        Returns:
            The master dataframe
        """
        logger.info("\n" + "=" * 60)
        logger.info("STARTING ETL PIPELINE")
        logger.info("=" * 60)
        
        try:
            processed_dataframes = []
            
            # Process Schema A files (crypto_posts)
            if self.schema_a_files:
                df_schema_a = self.process_schema_a_posts(self.schema_a_files)
                if not df_schema_a.empty:
                    processed_dataframes.append(df_schema_a)
            
            # Process Schema B files (reddit_posts)
            if self.schema_b_files:
                df_schema_b = self.process_schema_b_submissions(self.schema_b_files)
                if not df_schema_b.empty:
                    processed_dataframes.append(df_schema_b)
            
            # Process Schema C files (crypto_comments)
            if self.schema_c_files:
                df_schema_c = self.process_schema_c_comments(self.schema_c_files)
                if not df_schema_c.empty:
                    processed_dataframes.append(df_schema_c)
            
            # Consolidate and Clean
            self.master_df = self.consolidate_and_clean(processed_dataframes)
            
            # Save to CSV
            logger.info(f"\nSaving master dataset to: {output_path}")
            self.master_df.to_csv(output_path, index=False)
            logger.info(f"Successfully saved to: {os.path.abspath(output_path)}")
            
            # Final statistics
            logger.info("\n" + "=" * 60)
            logger.info("ETL PIPELINE COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"Total records: {len(self.master_df):,}")
            logger.info(f"Posts: {len(self.master_df[self.master_df['source_type'] == 'post']):,}")
            logger.info(f"Comments: {len(self.master_df[self.master_df['source_type'] == 'comment']):,}")
            
            # Display sample statistics
            logger.info("\nDataset Statistics:")
            logger.info(f"Date range: {self.master_df['created_date'].min()} to {self.master_df['created_date'].max()}")
            logger.info(f"Unique authors: {self.master_df['author'].nunique():,}")
            logger.info(f"Unique subreddits: {self.master_df['subreddit'].nunique()}")
            
            logger.info(f"\nTop 10 Subreddits by volume:")
            subreddit_counts = self.master_df['subreddit'].value_counts()
            for subreddit, count in subreddit_counts.head(10).items():
                logger.info(f"  {subreddit}: {count:,}")
            
            logger.info("\n" + "=" * 60)
            
            return self.master_df
            
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {e}")
            raise


# Main execution
if __name__ == "__main__":
    # SIMPLE USAGE: Just provide the directory path
    # The script will automatically find and process all files based on their names:
    # - crypto_posts*.csv → Schema A (Posts)
    # - reddit_posts*.csv → Schema B (Submissions)
    # - crypto_comments*.csv → Schema C (Comments)

    DATA_DIRECTORY = 'data_consolidation\\raw_sources'  # Change this to your directory path
    OUTPUT_PATH = 'master_dataset.csv'
    
    try:
        # Initialize ETL pipeline (automatic file discovery)
        etl = RedditDataETL(DATA_DIRECTORY)
        
        # Run the complete ETL process
        master_dataset = etl.run_etl(OUTPUT_PATH)
        
        # Display preview
        print("\n" + "=" * 60)
        print("MASTER DATASET PREVIEW")
        print("=" * 60)
        print("\nFirst 5 rows:")
        print(master_dataset.head().to_string())
        
        print(f"\nDataset shape: {master_dataset.shape}")
        print("\nColumn data types:")
        print(master_dataset.dtypes)
        
        print("\n" + "=" * 60)
        print("SUCCESS! Master dataset created successfully.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n{'='*60}")
        print("ERROR!")
        print("="*60)
        print(f"Failed to create master dataset: {e}")
        print("="*60)