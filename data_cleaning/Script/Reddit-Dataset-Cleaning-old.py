"""
Reddit Dataset Cleaning Script
===============================
Purpose: Clean Reddit posts/comments dataset by removing noise, spam, and bot-like behavior
Input: Reads from data/bronze/reddit/ (partitioned by date)
Output: Saves to data/silver/reddit/ with checkpoint and summary JSON files
"""
import pandas as pd
import re
import logging
import json
import os
from datetime import datetime
from pathlib import Path

# Configure loggingarret
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================
# Define paths
BASE_DIR = Path(__file__).parent.parent.parent  # Go to project root
SILVER_DIR = BASE_DIR / "data" / "silver" / "reddit"
OUTPUT_CSV = SILVER_DIR / "cleaned_reddit_dataset.csv"
CHECKPOINT_FILE = SILVER_DIR / "checkpoint.json"
SUMMARY_FILE = SILVER_DIR / "summary.json"

# Create silver directory structure
SILVER_DIR.mkdir(parents=True, exist_ok=True)
logger.info(f"Silver directory created/verified: {SILVER_DIR}")

# ============================================================================
# CHECKPOINT MANAGEMENT
# ============================================================================
def load_checkpoint():
    """Load checkpoint to track processed data"""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
            logger.info(f" Loaded checkpoint: {len(checkpoint.get('processed_ids', []))} IDs already processed")
            return checkpoint
    logger.info(" No checkpoint found - starting fresh")
    return {
        'processed_ids': [],
        'last_run': None,
        'total_processed': 0
    }

def save_checkpoint(processed_ids, stats):
    """Save checkpoint with processed IDs and statistics"""
    checkpoint = {
        'processed_ids': list(processed_ids),
        'last_run': datetime.now().isoformat(),
        'total_processed': len(processed_ids),
        'stats': stats
    }
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    logger.info(f" Checkpoint saved: {len(processed_ids)} processed IDs")

def save_summary(summary_data):
    """Save summary statistics to JSON"""
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    logger.info(f" Summary saved to: {SUMMARY_FILE}")

# ============================================================================
# FUNCTION TO LOAD BRONZE DATA BY DATE
# ============================================================================
def load_bronze_data_by_date(execution_date):
    """
    Load Reddit data from bronze layer for a specific execution date

    Args:
        execution_date: datetime object representing the extraction date

    Returns:
        DataFrame with Reddit data for that date
    """
    bronze_path = BASE_DIR / "data" / "bronze" / "reddit" / f"year={execution_date.year}" / f"month={execution_date.month:02d}" / f"day={execution_date.day:02d}"

    logger.info(f" Looking for bronze data in: {bronze_path}")

    if not bronze_path.exists():
        logger.warning(f" Bronze directory not found: {bronze_path}")
        return pd.DataFrame()

    # Find all parquet files in the directory
    parquet_files = list(bronze_path.glob("*.parquet"))

    if not parquet_files:
        logger.warning(f" No parquet files found in: {bronze_path}")
        return pd.DataFrame()

    logger.info(f" Found {len(parquet_files)} parquet file(s)")

    # Load all parquet files
    dfs = []
    for parquet_file in parquet_files:
        logger.info(f" Loading: {parquet_file.name}")
        df_temp = pd.read_parquet(parquet_file)
        dfs.append(df_temp)

    # Combine all dataframes
    df = pd.concat(dfs, ignore_index=True) if len(dfs) > 1 else dfs[0]
    logger.info(f" Loaded {len(df):,} rows from bronze layer")

    return df


# ============================================================================
# MAIN CLEANING FUNCTION
# ============================================================================
def clean_reddit_data(execution_date=None):
    """
    Main cleaning function that can be called with an execution_date

    Args:
        execution_date: datetime object (optional, defaults to today)

    Returns:
        Dictionary with cleaning statistics
    """
    if execution_date is None:
        execution_date = datetime.now()

    logger.info("=" * 80)
    logger.info("REDDIT DATASET CLEANING PIPELINE STARTED")
    logger.info(f"Execution date: {execution_date.strftime('%Y-%m-%d')}")
    logger.info("=" * 80)
    logger.info("[STEP 1] Loading dataset and checkpoint...")

    # Load checkpoint
    checkpoint = load_checkpoint()
    processed_ids = set(checkpoint.get('processed_ids', []))

    # Load the Reddit dataset FROM BRONZE LAYER
    df = load_bronze_data_by_date(execution_date)

    if df.empty:
        logger.warning(" No data found in bronze layer for this date!")
        return {
            'initial_rows': 0,
            'final_rows': 0,
            'removed_rows': 0,
            'removal_rate': 0.0
        }

    # Display initial statistics
    logger.info(f" Initial Dataset Statistics: {len(df):,} rows, {len(df.columns)} columns")
    logger.debug(f"Columns: {list(df.columns)}")
    logger.debug(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    # Filter out already processed IDs
    if processed_ids and 'unified_id' in df.columns:
        initial_count_before_filter = len(df)
        df = df[~df['unified_id'].isin(processed_ids)]
        logger.info(f" Filtered out {initial_count_before_filter - len(df):,} already processed rows")

        if len(df) == 0:
            logger.info(" No new data to process. All data already processed!")
            return {
                'initial_rows': initial_count_before_filter,
                'final_rows': 0,
                'removed_rows': 0,
                'removal_rate': 0.0,
                'already_processed': initial_count_before_filter
            }

    # Store initial count for comparison
    initial_count = len(df)
    logger.info(f"New data to process: {initial_count:,} rows")

    # ============================================================================
    # STEP 2: DATA TYPE VALIDATION & PARSING
    # ============================================================================
    logger.info("[STEP 2] Validating data types and parsing dates...")

# Ensure required columns exist
required_columns = [
    'unified_id', 'text_content', 'created_date', 'author',
    'source_type', 'subreddit', 'crypto_mentions', 'source_platform'
]
missing_cols = set(required_columns) - set(df.columns)
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")

# Parse created_date as datetime
df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')

# Check for invalid dates
invalid_dates = df['created_date'].isna().sum()
if invalid_dates > 0:
    logger.warning(f"Found {invalid_dates} invalid dates - removing these rows")
    df = df.dropna(subset=['created_date'])

logger.info(f" Date range: {df['created_date'].min()} to {df['created_date'].max()}")

# ============================================================================
# STEP 3: HANDLE MISSING VALUES
# ============================================================================
logger.info("[STEP 3] Handling missing values...")

# Check missing values per column
missing_summary = df.isnull().sum()
for col, count in missing_summary[missing_summary > 0].items():
    logger.debug(f"Missing values in {col}: {count} ({count/len(df)*100:.2f}%)")

# Drop rows with missing critical fields
critical_fields = ['unified_id', 'text_content', 'author', 'source_type']
before_missing = len(df)
df = df.dropna(subset=critical_fields)
removed_missing = before_missing - len(df)
if removed_missing > 0:
    logger.info(f" Removed {removed_missing} rows with missing critical fields")

# Fill non-critical missing values
df['subreddit'] = df['subreddit'].fillna('unknown')

# Handle crypto_mentions
if 'crypto_mentions' not in df.columns:
    df['crypto_mentions'] = None
else:
    df['crypto_mentions'] = df['crypto_mentions'].astype(object)
    df['crypto_mentions'] = df['crypto_mentions'].where(df['crypto_mentions'].notna(), None)

# ============================================================================
# STEP 4: BASIC TEXT FILTERS
# ============================================================================
logger.info("[STEP 4] Applying basic text filters...")

# Remove posts shorter than 10 characters
before_short = len(df)
df = df[df['text_content'].str.len() >= 10]
removed_short = before_short - len(df)
logger.info(f" Removed {removed_short} posts shorter than 10 characters")

# Remove exact duplicates
before_dupes = len(df)
df = df.drop_duplicates(subset=['text_content', 'created_date'], keep='first')
removed_dupes = before_dupes - len(df)
logger.info(f"Removed {removed_dupes} exact duplicate posts")

# ============================================================================
# STEP 5: BOT DETECTION & REMOVAL
# ============================================================================
logger.info("[STEP 5] Detecting and removing bot accounts...")

# Define bot name patterns
bot_patterns = [
    r'.*bot.*', r'auto.*', r'.*airdrop.*', r'crypto.*airdrop.*',
    r'.*moderator.*', r'.*_bot$', r'^bot_.*', r'.*automoderator.*'
]
bot_regex = '|'.join(bot_patterns)

# Identify bot accounts
bot_mask = df['author'].str.lower().str.match(bot_regex, na=False)
bot_count = bot_mask.sum()
bot_authors = df[bot_mask]['author'].unique()
logger.info(f"Identified {bot_count} posts from {len(bot_authors)} bot accounts")
if len(bot_authors) <= 20:
    logger.debug(f"Bot accounts: {', '.join(bot_authors[:20])}")

# Remove bot accounts
df = df[~bot_mask]
logger.info(f" Removed {bot_count} bot-generated posts")

# ============================================================================
# STEP 6: SPAM & HIGH-FREQUENCY POSTER DETECTION
# ============================================================================
logger.info("[STEP 6] Detecting spam and high-frequency posters...")

# Calculate posts per day per author
df['date_only'] = df['created_date'].dt.date
posts_per_day = df.groupby(['author', 'date_only']).size().reset_index(name='daily_post_count')

# Identify accounts posting more than 50 times per day
spam_accounts = posts_per_day[posts_per_day['daily_post_count'] > 50]['author'].unique()
logger.info(f" Found {len(spam_accounts)} accounts posting >50 times/day")

# Remove spam accounts
before_spam = len(df)
df = df[~df['author'].isin(spam_accounts)]
removed_spam = before_spam - len(df)
logger.info(f" Removed {removed_spam} posts from high-frequency spammers")

# Detect repeated spam messages
text_frequency = df.groupby('text_content')['author'].nunique().reset_index(name='unique_authors')
text_counts = df.groupby('text_content').size().reset_index(name='total_count')
spam_text_analysis = text_frequency.merge(text_counts, on='text_content')

# Flag texts posted by 5+ different users
spam_texts = spam_text_analysis[
    (spam_text_analysis['unique_authors'] >= 5) &
    (spam_text_analysis['total_count'] >= 10)
]['text_content'].tolist()

before_repeated_spam = len(df)
df = df[~df['text_content'].isin(spam_texts)]
removed_repeated_spam = before_repeated_spam - len(df)
logger.info(f" Removed {removed_repeated_spam} repeated spam messages")

# Drop temporary column
df = df.drop(columns=['date_only'])

# ============================================================================
# STEP 7: CLEAN TEXT CONTENT
# ============================================================================
logger.info("[STEP 7] Cleaning text content...")

# Function to remove URLs
def remove_urls(text):
    if pd.isna(text):
        return text
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(url_pattern, '', text)

# Function to remove excessive emojis
def remove_excessive_emojis(text):
    if pd.isna(text):
        return text
    emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]{6,}'
    return re.sub(emoji_pattern, '', text)

# Apply text cleaning
logger.info("Removing URLs...")
df['text_content'] = df['text_content'].apply(remove_urls)
logger.info("Removing excessive emojis...")
df['text_content'] = df['text_content'].apply(remove_excessive_emojis)

# Remove extra whitespace
df['text_content'] = df['text_content'].str.strip()
df['text_content'] = df['text_content'].str.replace(r'\s+', ' ', regex=True)

# Remove posts that became too short after cleaning
before_clean_short = len(df)
df = df[df['text_content'].str.len() >= 10]
removed_clean_short = before_clean_short - len(df)
if removed_clean_short > 0:
    logger.info(f" Removed {removed_clean_short} posts that became too short after cleaning")

# ============================================================================
# STEP 8: FINAL VALIDATION
# ============================================================================
logger.info("[STEP 8] Final validation...")

# Check for any remaining null values in critical columns
remaining_nulls = df[critical_fields].isnull().sum().sum()
if remaining_nulls > 0:
    logger.warning(f" {remaining_nulls} null values remain in critical fields")
    df = df.dropna(subset=critical_fields)

# Verify data types
logger.info(" Verified data types:")
logger.debug(f"unified_id: {df['unified_id'].dtype}")
logger.debug(f"created_date: {df['created_date'].dtype}")
logger.debug(f"author: {df['author'].dtype}")

# ============================================================================
# STEP 9: MERGE WITH EXISTING DATA & SAVE
# ============================================================================
logger.info("[STEP 9] Merging with existing data and saving...")

# Reset index
df = df.reset_index(drop=True)

# Load existing CSV if it exists and append new data
if OUTPUT_CSV.exists():
    logger.info(f"Loading existing data from {OUTPUT_CSV}")
    existing_df = pd.read_csv(OUTPUT_CSV)
    logger.info(f" Existing data: {len(existing_df):,} rows")

    # Combine old and new data
    combined_df = pd.concat([existing_df, df], ignore_index=True)

    # Remove any duplicates that might have slipped through
    before_final_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['unified_id'], keep='first')
    final_dedup_removed = before_final_dedup - len(combined_df)
    if final_dedup_removed > 0:
        logger.info(f" Removed {final_dedup_removed} duplicates during merge")

    df_to_save = combined_df
    logger.info(f" Combined dataset: {len(df_to_save):,} rows")
else:
    df_to_save = df
    logger.info(f" Creating new dataset with {len(df_to_save):,} rows")

# Save to CSV
df_to_save.to_csv(OUTPUT_CSV, index=False)
logger.info(f" Saved cleaned dataset to: {OUTPUT_CSV}")

# ============================================================================
# STEP 10: UPDATE CHECKPOINT
# ============================================================================
logger.info("[STEP 10] Updating checkpoint...")

# Add new processed IDs to checkpoint
new_processed_ids = set(df['unified_id'].tolist())
all_processed_ids = processed_ids.union(new_processed_ids)

# Calculate removal statistics for this run
final_count = len(df)
total_removed = initial_count - final_count
removal_rate = (total_removed / initial_count * 100) if initial_count > 0 else 0

checkpoint_stats = {
    'this_run': {
        'timestamp': datetime.now().isoformat(),
        'initial_rows': initial_count,
        'final_rows': final_count,
        'removed_rows': total_removed,
        'removal_rate_percent': round(removal_rate, 2)
    },
    'cumulative': {
        'total_processed_ids': len(all_processed_ids),
        'total_rows_in_output': len(df_to_save)
    }
}

save_checkpoint(all_processed_ids, checkpoint_stats)

# ============================================================================
# STEP 11: GENERATE SUMMARY JSON
# ============================================================================
logger.info("[STEP 11] Generating summary JSON...")

summary_data = {
    'metadata': {
        'generated_at': datetime.now().isoformat(),
        'input_file': str(INPUT_FILE),
        'output_file': str(OUTPUT_CSV),
        'checkpoint_file': str(CHECKPOINT_FILE)
    },
    'processing_stats': {
        'this_run': {
            'new_rows_processed': initial_count,
            'rows_after_cleaning': final_count,
            'rows_removed': total_removed,
            'removal_rate_percent': round(removal_rate, 2),
            'breakdown': {
                'invalid_dates': int(invalid_dates),
                'missing_critical_fields': int(removed_missing),
                'too_short': int(removed_short),
                'exact_duplicates': int(removed_dupes),
                'bot_accounts': int(bot_count),
                'high_frequency_posters': int(removed_spam),
                'repeated_spam': int(removed_repeated_spam),
                'post_cleaning_short': int(removed_clean_short)
            }
        },
        'cumulative': {
            'total_processed_ids': len(all_processed_ids),
            'total_rows_in_output': len(df_to_save),
            'unique_authors': int(df_to_save['author'].nunique()),
            'unique_subreddits': int(df_to_save['subreddit'].nunique()),
            'posts_count': int((df_to_save['source_type'] == 'post').sum()),
            'comments_count': int((df_to_save['source_type'] == 'comment').sum())
        }
    },
    'data_quality': {
        'date_range': {
            'min': str(df_to_save['created_date'].min()),
            'max': str(df_to_save['created_date'].max())
        },
        'text_statistics': {
            'avg_length': round(df_to_save['text_content'].str.len().mean(), 1),
            'min_length': int(df_to_save['text_content'].str.len().min()),
            'max_length': int(df_to_save['text_content'].str.len().max())
        },
        'memory_usage_mb': round(df_to_save.memory_usage(deep=True).sum() / 1024**2, 2)
    }
}

save_summary(summary_data)

# ============================================================================
# STEP 12: DISPLAY SUMMARY
# ============================================================================
logger.info("=" * 80)
logger.info("CLEANING SUMMARY")
logger.info("=" * 80)

logger.info(f"\n This Run Statistics:")
logger.info(f"New rows processed:  {initial_count:,}")
logger.info(f"Rows after cleaning: {final_count:,}")
logger.info(f"Rows removed:        {total_removed:,} ({removal_rate:.2f}%)")

logger.info(f"\nBreakdown of Removed Rows:")
logger.info(f"Invalid dates:       {invalid_dates:,}")
logger.info(f"Missing critical:    {removed_missing:,}")
logger.info(f"Too short (<10 chr): {removed_short:,}")
logger.info(f"Exact duplicates:    {removed_dupes:,}")
logger.info(f"Bot accounts:        {bot_count:,}")
logger.info(f"High-freq posters:   {removed_spam:,}")
logger.info(f"Repeated spam:       {removed_repeated_spam:,}")
logger.info(f"Post-cleaning short: {removed_clean_short:,}")

logger.info(f"\nCumulative Dataset Statistics:")
logger.info(f"Total rows:          {len(df_to_save):,}")
logger.info(f"Total processed IDs: {len(all_processed_ids):,}")
logger.info(f"Unique authors:      {df_to_save['author'].nunique():,}")
logger.info(f"Unique subreddits:   {df_to_save['subreddit'].nunique():,}")
logger.info(f"Posts:               {(df_to_save['source_type'] == 'post').sum():,}")
logger.info(f"Comments:            {(df_to_save['source_type'] == 'comment').sum():,}")
logger.info(f"Date range:          {df_to_save['created_date'].min()} to {df_to_save['created_date'].max()}")
logger.info(f"Avg text length:     {df_to_save['text_content'].str.len().mean():.1f} characters")
logger.info(f"Memory usage:        {df_to_save.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

logger.info("\n" + "=" * 80)
logger.info(" CLEANING PIPELINE COMPLETED SUCCESSFULLY")
logger.info("=" * 80)
logger.info(f"\n Output files:")
logger.info(f"  - CSV: {OUTPUT_CSV}")
logger.info(f"  - Checkpoint: {CHECKPOINT_FILE}")
logger.info(f"  - Summary: {SUMMARY_FILE}")
logger.info("Dataset is ready for NLP analysis!")
