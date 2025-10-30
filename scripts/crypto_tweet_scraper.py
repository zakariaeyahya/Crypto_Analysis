"""
Crypto Tweet Scraper - Fresh Tweets Only
Collects only NEW crypto-related tweets on each run using persistent tracking
Filters spam/bot accounts and exports to CSV/JSON
"""

import snscrape.modules.twitter as sntwitter
import pandas as pd
import json
from datetime import datetime, timedelta
from collections import Counter
import re
import time
import os
import pickle

# Configuration
OUTPUT_FORMAT = "csv"  # Choose "csv" or "json"
OUTPUT_FILENAME = "crypto_tweets"
MAX_TWEETS_PER_QUERY = 1000  # Limit per search query to manage data volume
TRACKING_FILE = "collected_tweet_ids.pkl"  # File to store previously collected tweet IDs

# Define search terms and hashtags
SEARCH_TERMS = [
    "#Bitcoin",
    "#Ethereum",
    "$BTC",
    "$ETH",
    '"crypto bullish"',  # Exact phrase
    '"crypto bearish"',  # Exact phrase
    "Bitcoin",
    "Ethereum",
]

# Spam/Bot detection thresholds
SPAM_FILTERS = {
    "min_followers": 10,  # Accounts with fewer followers likely bots
    "max_tweets_per_day": 100,  # Extremely high posting frequency
    "min_account_age_days": 30,  # Very new accounts often spam
    "repeated_text_threshold": 0.8,  # If 80%+ tweets identical, likely bot
}


def load_collected_tweet_ids():
    """
    Load the set of previously collected tweet IDs from disk
    Returns:
        set: Set of tweet IDs that have been collected before
    """
    if os.path.exists(TRACKING_FILE):
        try:
            with open(TRACKING_FILE, 'rb') as f:
                collected_ids = pickle.load(f)
            print(f"Loaded {len(collected_ids)} previously collected tweet IDs")
            return collected_ids
        except Exception as e:
            print(f"Error loading tracking file: {e}")
            return set()
    else:
        print("No previous collection found - starting fresh")
        return set()


def save_collected_tweet_ids(collected_ids):
    """
    Save the set of collected tweet IDs to disk for future runs
    Args:
        collected_ids: Set of tweet IDs
    """
    try:
        with open(TRACKING_FILE, 'wb') as f:
            pickle.dump(collected_ids, f)
        print(f"Saved {len(collected_ids)} tweet IDs to tracking file")
    except Exception as e:
        print(f"Error saving tracking file: {e}")


def clean_old_tracking_data(collected_ids, max_age_days=60):
    """
    Remove tweet IDs older than max_age_days to prevent tracking file from growing indefinitely
    This keeps the tracking file manageable while still preventing duplicates
    Args:
        collected_ids: Set of tweet IDs with timestamps
        max_age_days: Maximum age to keep in days
    Returns:
        set: Cleaned set of tweet IDs
    """
    # Note: Since we only store IDs, we'll keep all for now
    # In production, you might store (id, timestamp) tuples
    return collected_ids


def calculate_date_range():
    """
    Calculate the date range for the past 30 days
    Returns: tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def is_spam_account(tweet):
    """
    Detect potential spam or bot accounts based on multiple criteria
    Args:
        tweet: Tweet object from snscrape
    Returns:
        bool: True if account appears to be spam/bot, False otherwise
    """
    user = tweet.user
    
    # Filter 1: Check follower count
    if user.followersCount < SPAM_FILTERS["min_followers"]:
        return True
    
    # Filter 2: Check account age
    account_age = (datetime.now() - user.created).days
    if account_age < SPAM_FILTERS["min_account_age_days"]:
        return True
    
    # Filter 3: Check posting frequency (tweets per day)
    if account_age > 0:
        tweets_per_day = user.statusesCount / account_age
        if tweets_per_day > SPAM_FILTERS["max_tweets_per_day"]:
            return True
    
    # Filter 4: Check for suspicious username patterns (e.g., many numbers)
    username = user.username.lower()
    digit_ratio = sum(c.isdigit() for c in username) / len(username)
    if digit_ratio > 0.7:  # More than 70% digits in username
        return True
    
    return False


def has_repeated_content(tweet_text, text_history):
    """
    Check if tweet content is repetitive/spam
    Args:
        tweet_text: Current tweet text
        text_history: Counter object tracking text frequency
    Returns:
        bool: True if content appears repetitive
    """
    # Normalize text (remove URLs, mentions, extra spaces)
    normalized_text = re.sub(r'http\S+|@\w+', '', tweet_text)
    normalized_text = ' '.join(normalized_text.split()).lower()
    
    # Update frequency counter
    text_history[normalized_text] += 1
    
    # Check if this exact text appears too frequently
    if text_history[normalized_text] > 3:  # Same text more than 3 times
        return True
    
    return False


def scrape_tweets(search_term, start_date, end_date, text_history, collected_ids):
    """
    Scrape tweets for a given search term within date range
    Only collects tweets that haven't been collected before
    Args:
        search_term: Query string to search
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        text_history: Counter for tracking repeated content
        collected_ids: Set of previously collected tweet IDs
    Returns:
        list: List of dictionaries containing NEW tweet data
    """
    tweets_data = []
    
    # Construct Twitter search query with date filters
    query = f"{search_term} since:{start_date} until:{end_date} lang:en"
    
    print(f"\nScraping tweets for: {search_term}")
    print(f"Query: {query}")
    
    try:
        # Scrape tweets using TwitterSearchScraper
        tweet_count = 0
        new_tweet_count = 0
        skipped_duplicate_count = 0
        
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            # Limit tweets per query to avoid excessive data
            if i >= MAX_TWEETS_PER_QUERY:
                break
            
            # CRITICAL: Skip if tweet was already collected
            if tweet.id in collected_ids:
                skipped_duplicate_count += 1
                continue
            
            # Apply spam/bot filters
            if is_spam_account(tweet):
                continue
            
            # Check for repeated content
            if has_repeated_content(tweet.rawContent, text_history):
                continue
            
            # Extract relevant tweet data
            tweet_data = {
                "tweet_id": tweet.id,
                "username": tweet.user.username,
                "display_name": tweet.user.displayname,
                "date": tweet.date.strftime("%Y-%m-%d %H:%M:%S"),
                "tweet_text": tweet.rawContent,
                "like_count": tweet.likeCount,
                "retweet_count": tweet.retweetCount,
                "reply_count": tweet.replyCount,
                "link": tweet.url,
                "search_term": search_term,  # Track which query found this tweet
                "follower_count": tweet.user.followersCount,  # Additional context
                "verified": tweet.user.verified,  # Verified accounts less likely spam
            }
            
            tweets_data.append(tweet_data)
            new_tweet_count += 1
            
            # Progress indicator
            if new_tweet_count % 50 == 0:
                print(f"  Collected {new_tweet_count} NEW tweets...")
        
        print(f"  New tweets collected: {new_tweet_count}")
        print(f"  Skipped (already collected): {skipped_duplicate_count}")
        
    except Exception as e:
        print(f"  Error scraping {search_term}: {str(e)}")
    
    return tweets_data


def remove_duplicates(tweets_data):
    """
    Remove duplicate tweets (same tweet ID) within current collection
    Args:
        tweets_data: List of tweet dictionaries
    Returns:
        list: Deduplicated list of tweets
    """
    seen_ids = set()
    unique_tweets = []
    
    for tweet in tweets_data:
        if tweet["tweet_id"] not in seen_ids:
            seen_ids.add(tweet["tweet_id"])
            unique_tweets.append(tweet)
    
    return unique_tweets


def save_data(tweets_data, format_type="csv"):
    """
    Save collected tweets to CSV or JSON file with timestamp
    Args:
        tweets_data: List of tweet dictionaries
        format_type: "csv" or "json"
    """
    if not tweets_data:
        print("\nNo NEW tweets to save!")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format_type == "csv":
        # Convert to pandas DataFrame for easy CSV export
        df = pd.DataFrame(tweets_data)
        filename = f"{OUTPUT_FILENAME}_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\nData saved to {filename}")
        print(f"Total NEW tweets: {len(df)}")
        print(f"\nSample statistics:")
        print(f"  Average likes: {df['like_count'].mean():.2f}")
        print(f"  Average retweets: {df['retweet_count'].mean():.2f}")
        print(f"  Unique users: {df['username'].nunique()}")
        
    elif format_type == "json":
        filename = f"{OUTPUT_FILENAME}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tweets_data, f, indent=2, ensure_ascii=False)
        print(f"\nData saved to {filename}")
        print(f"Total NEW tweets: {len(tweets_data)}")


def append_to_master_file(tweets_data, format_type="csv"):
    """
    Append new tweets to a master cumulative file
    Args:
        tweets_data: List of new tweet dictionaries
        format_type: "csv" or "json"
    """
    if not tweets_data:
        return
    
    master_filename = f"{OUTPUT_FILENAME}_master.{format_type}"
    
    if format_type == "csv":
        df_new = pd.DataFrame(tweets_data)
        
        # Check if master file exists
        if os.path.exists(master_filename):
            # Append to existing file
            df_new.to_csv(master_filename, mode='a', header=False, index=False, encoding='utf-8')
            print(f"Appended {len(df_new)} tweets to {master_filename}")
        else:
            # Create new master file
            df_new.to_csv(master_filename, index=False, encoding='utf-8')
            print(f"Created new master file: {master_filename}")
    
    elif format_type == "json":
        # For JSON, we need to load existing data, append, and rewrite
        existing_data = []
        if os.path.exists(master_filename):
            with open(master_filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        existing_data.extend(tweets_data)
        
        with open(master_filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"Updated master file: {master_filename} (Total: {len(existing_data)} tweets)")


def main():
    """
    Main execution function - collects only fresh tweets
    """
    print("=" * 60)
    print("Crypto Tweet Scraper - FRESH TWEETS ONLY")
    print("=" * 60)
    
    # Load previously collected tweet IDs
    collected_ids = load_collected_tweet_ids()
    
    # Calculate date range for past 30 days
    start_date, end_date = calculate_date_range()
    print(f"\nDate range: {start_date} to {end_date}")
    
    # Initialize text history counter for duplicate detection
    text_history = Counter()
    
    # Collect all tweets
    all_tweets = []
    
    for search_term in SEARCH_TERMS:
        # Scrape tweets for each search term (only new ones)
        tweets = scrape_tweets(search_term, start_date, end_date, text_history, collected_ids)
        all_tweets.extend(tweets)
        
        # Small delay to be respectful to rate limits
        time.sleep(1)
    
    # Remove duplicate tweets within current collection
    print("\nRemoving duplicates within current collection...")
    unique_tweets = remove_duplicates(all_tweets)
    print(f"Before deduplication: {len(all_tweets)} tweets")
    print(f"After deduplication: {len(unique_tweets)} tweets")
    
    if unique_tweets:
        # Update collected IDs set with new tweet IDs
        new_ids = {tweet["tweet_id"] for tweet in unique_tweets}
        collected_ids.update(new_ids)
        
        # Save updated tracking file
        save_collected_tweet_ids(collected_ids)
        
        # Save data to timestamped file
        save_data(unique_tweets, format_type=OUTPUT_FORMAT)
        
        # Also append to master cumulative file
        append_to_master_file(unique_tweets, format_type=OUTPUT_FORMAT)
    else:
        print("\n⚠️  No new tweets found in this run!")
        print("This could mean:")
        print("  - All recent tweets were already collected")
        print("  - No new tweets match your search criteria")
        print("  - Try running again later for fresh content")
    
    print("\n" + "=" * 60)
    print("Collection Complete!")
    print(f"Total unique tweets tracked: {len(collected_ids)}")
    print("=" * 60)


if __name__ == "__main__":
    main()