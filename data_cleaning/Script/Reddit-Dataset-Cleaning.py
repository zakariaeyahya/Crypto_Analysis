"""
Reddit Dataset Cleaning Script
===============================
Purpose: Clean Reddit posts/comments dataset by removing noise, spam, and bot-like behavior
Output: master_dataset.csv (high-quality cleaned dataset)
"""
import pandas as pd
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ============================================================================
# STEP 1: LOAD DATASET
# ============================================================================
logger.info("REDDIT DATASET CLEANING PIPELINE STARTED")
logger.info("[STEP 1] Loading dataset...")

# Load the Reddit dataset
df = pd.read_csv(r"data_consolidation\outputs\master_dataset.csv")

# Display initial statistics
logger.info(f"📊 Initial Dataset Statistics: {len(df):,} rows, {len(df.columns)} columns")
logger.debug(f"Columns: {list(df.columns)}")
logger.debug(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Store initial count for comparison
initial_count = len(df)

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

logger.info(f"📅 Date range: {df['created_date'].min()} to {df['created_date'].max()}")

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
    logger.info(f"✂️ Removed {removed_missing} rows with missing critical fields")

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
logger.info(f"✂️ Removed {removed_short} posts shorter than 10 characters")

# Remove exact duplicates
before_dupes = len(df)
df = df.drop_duplicates(subset=['text_content', 'created_date'], keep='first')
removed_dupes = before_dupes - len(df)
logger.info(f"✂️ Removed {removed_dupes} exact duplicate posts")

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
logger.info(f"🤖 Identified {bot_count} posts from {len(bot_authors)} bot accounts")
if len(bot_authors) <= 20:
    logger.debug(f"Bot accounts: {', '.join(bot_authors[:20])}")

# Remove bot accounts
df = df[~bot_mask]
logger.info(f"✂️ Removed {bot_count} bot-generated posts")

# ============================================================================
# STEP 6: SPAM & HIGH-FREQUENCY POSTER DETECTION
# ============================================================================
logger.info("[STEP 6] Detecting spam and high-frequency posters...")

# Calculate posts per day per author
df['date_only'] = df['created_date'].dt.date
posts_per_day = df.groupby(['author', 'date_only']).size().reset_index(name='daily_post_count')

# Identify accounts posting more than 50 times per day
spam_accounts = posts_per_day[posts_per_day['daily_post_count'] > 50]['author'].unique()
logger.info(f"📢 Found {len(spam_accounts)} accounts posting >50 times/day")

# Remove spam accounts
before_spam = len(df)
df = df[~df['author'].isin(spam_accounts)]
removed_spam = before_spam - len(df)
logger.info(f"✂️ Removed {removed_spam} posts from high-frequency spammers")

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
logger.info(f"✂️ Removed {removed_repeated_spam} repeated spam messages")

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
logger.info("🧹 Removing URLs...")
df['text_content'] = df['text_content'].apply(remove_urls)
logger.info("🧹 Removing excessive emojis...")
df['text_content'] = df['text_content'].apply(remove_excessive_emojis)

# Remove extra whitespace
df['text_content'] = df['text_content'].str.strip()
df['text_content'] = df['text_content'].str.replace(r'\s+', ' ', regex=True)

# Remove posts that became too short after cleaning
before_clean_short = len(df)
df = df[df['text_content'].str.len() >= 10]
removed_clean_short = before_clean_short - len(df)
if removed_clean_short > 0:
    logger.info(f"✂️ Removed {removed_clean_short} posts that became too short after cleaning")

# ============================================================================
# STEP 8: FINAL VALIDATION
# ============================================================================
logger.info("[STEP 8] Final validation...")

# Check for any remaining null values in critical columns
remaining_nulls = df[critical_fields].isnull().sum().sum()
if remaining_nulls > 0:
    logger.warning(f"⚠️ {remaining_nulls} null values remain in critical fields")
    df = df.dropna(subset=critical_fields)

# Verify data types
logger.info("✅ Verified data types:")
logger.debug(f"unified_id: {df['unified_id'].dtype}")
logger.debug(f"created_date: {df['created_date'].dtype}")
logger.debug(f"author: {df['author'].dtype}")

# ============================================================================
# STEP 9: SAVE CLEANED DATASET
# ============================================================================
logger.info("[STEP 9] Saving cleaned dataset...")

# Reset index
df = df.reset_index(drop=True)

# Save to CSV
output_file = r'D:\S9_Projects\Sentiment analysis for crypto markets\Repo\Crypto_Analysis\data_cleaning\output\cleaned_master_dataset1.csv'
df.to_csv(output_file, index=False)
logger.info(f"💾 Saved cleaned dataset to: {output_file}")

# ============================================================================
# STEP 10: SUMMARY STATISTICS
# ============================================================================
logger.info("=" * 80)
logger.info("CLEANING SUMMARY")
logger.info("=" * 80)

# Calculate removal statistics
final_count = len(df)
total_removed = initial_count - final_count
removal_rate = (total_removed / initial_count) * 100

logger.info(f"\n📊 Overall Statistics:")
logger.info(f"Initial rows:        {initial_count:,}")
logger.info(f"Final rows:          {final_count:,}")
logger.info(f"Rows removed:        {total_removed:,} ({removal_rate:.2f}%)")
logger.info(f"Rows retained:       {final_count/initial_count*100:.2f}%")

logger.info(f"\n📋 Breakdown of Removed Rows:")
logger.info(f"Invalid dates:       {invalid_dates:,}")
logger.info(f"Missing critical:    {removed_missing:,}")
logger.info(f"Too short (<10 chr): {removed_short:,}")
logger.info(f"Exact duplicates:    {removed_dupes:,}")
logger.info(f"Bot accounts:        {bot_count:,}")
logger.info(f"High-freq posters:   {removed_spam:,}")
logger.info(f"Repeated spam:       {removed_repeated_spam:,}")
logger.info(f"Post-cleaning short: {removed_clean_short:,}")

logger.info(f"\n📈 Final Dataset Statistics:")
logger.info(f"Unique authors:      {df['author'].nunique():,}")
logger.info(f"Unique subreddits:   {df['subreddit'].nunique():,}")
logger.info(f"Posts:               {(df['source_type'] == 'post').sum():,}")
logger.info(f"Comments:            {(df['source_type'] == 'comment').sum():,}")
logger.info(f"Date range:          {df['created_date'].min()} to {df['created_date'].max()}")
logger.info(f"Avg text length:     {df['text_content'].str.len().mean():.1f} characters")
logger.info(f"Memory usage:        {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

logger.info("\n" + "=" * 80)
logger.info("✅ CLEANING PIPELINE COMPLETED SUCCESSFULLY")
logger.info("=" * 80)
logger.info(f"\n📁 Output file: {output_file}")
logger.info("🎯 Dataset is ready for NLP analysis!")
