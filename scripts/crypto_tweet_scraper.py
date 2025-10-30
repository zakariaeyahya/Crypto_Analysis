"""
Crypto Tweet Scraper - Using Twitter API v2 (Tweepy)
Collects only NEW crypto-related tweets on each run using official API
Requires Twitter API credentials (Free tier available)
"""

import tweepy
import pandas as pd
import json
from datetime import datetime, timedelta
from collections import Counter
import re
import time
import os
import pickle
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONFIGURATION - CREDENTIALS LOADED FROM .env FILE
# ============================================================================
# Get free API access at: https://developer.twitter.com/en/portal/dashboard
TWITTER_API_CONFIG = {
    "bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),  # Loaded from .env
}

# Output Configuration
OUTPUT_FORMAT = "csv"  # Choose "csv" or "json"
OUTPUT_FILENAME = "crypto_tweets"
MAX_TWEETS_PER_QUERY = 10  # FREE TIER: Reduced to 10 (you only get 100 reads/month!)
TRACKING_FILE = "collected_tweet_ids.pkl"
SEARCH_DAYS = 7  # Free tier: last 7 days only (upgrade to Academic for 30 days)

# FREE TIER WARNING
print("⚠️  WARNING: Free tier has only 100 tweet reads per month!")
print("   This script is optimized for BASIC ($100/mo) or ACADEMIC (free) tiers")
print("   Consider applying for Academic Research access for free unlimited access")

# Define search terms and hashtags
SEARCH_TERMS = [
    "#Bitcoin",
    "#Ethereum",
    "$BTC",
    "$ETH",
    '"crypto bullish"',
    '"crypto bearish"',
    "Bitcoin",
    "Ethereum",
]

# Spam/Bot detection thresholds
SPAM_FILTERS = {
    "min_followers": 10,
    "max_tweets_per_day": 100,
    "min_account_age_days": 30,
}


def initialize_twitter_client():
    """
    Initialize Twitter API v2 client with bearer token from .env file
    Returns:
        tweepy.Client: Authenticated Twitter client
    """
    bearer_token = TWITTER_API_CONFIG["bearer_token"]
    
    if not bearer_token:
        print("\n" + "="*60)
        print("ERROR: Twitter API credentials not found!")
        print("="*60)
        print("\nTo use this script, you need to:")
        print("1. Create a .env file in the same directory as this script")
        print("2. Add your Bearer Token to the .env file:")
        print("   TWITTER_BEARER_TOKEN=your_actual_bearer_token_here")
        print("\n3. Get your Bearer Token:")
        print("   • Go to: https://developer.twitter.com/en/portal/dashboard")
        print("   • Sign up for a free developer account")
        print("   • Create a new App and get your Bearer Token")
        print("\nFree tier limits: 500K tweets/month, perfect for this use case")
        print("="*60)
        exit(1)
    
    try:
        client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
        print("✓ Twitter API client initialized successfully")
        return client
    except Exception as e:
        print(f"Error initializing Twitter client: {e}")
        print("Please check your TWITTER_BEARER_TOKEN in the .env file")
        exit(1)


def load_collected_tweet_ids():
    """Load previously collected tweet IDs from disk"""
    if os.path.exists(TRACKING_FILE):
        try:
            with open(TRACKING_FILE, 'rb') as f:
                collected_ids = pickle.load(f)
            print(f"✓ Loaded {len(collected_ids)} previously collected tweet IDs")
            return collected_ids
        except Exception as e:
            print(f"Warning: Error loading tracking file: {e}")
            return set()
    else:
        print("✓ No previous collection found - starting fresh")
        return set()


def save_collected_tweet_ids(collected_ids):
    """Save collected tweet IDs to disk for future runs"""
    try:
        with open(TRACKING_FILE, 'wb') as f:
            pickle.dump(collected_ids, f)
        print(f"✓ Saved {len(collected_ids)} tweet IDs to tracking file")
    except Exception as e:
        print(f"Warning: Error saving tracking file: {e}")


def calculate_date_range():
    """
    Calculate date range based on API limitations
    Free tier: Last 7 days only
    Academic/Pro tier: Last 30 days (change SEARCH_DAYS to 30)
    Returns:
        tuple: (start_date, end_date) as datetime objects
    """
    end_date = datetime.utcnow() - timedelta(seconds=30)  # 30 seconds before now
    start_date = end_date - timedelta(days=SEARCH_DAYS)
    return start_date, end_date


def is_spam_account(user_metrics, user_created_at):
    """
    Detect potential spam/bot accounts
    Args:
        user_metrics: Dictionary with follower_count, tweet_count
        user_created_at: Account creation datetime
    Returns:
        bool: True if spam/bot detected
    """
    # Filter 1: Check follower count
    if user_metrics.get('followers_count', 0) < SPAM_FILTERS["min_followers"]:
        return True
    
    # Filter 2: Check account age
    account_age = (datetime.utcnow().replace(tzinfo=user_created_at.tzinfo) - user_created_at).days
    if account_age < SPAM_FILTERS["min_account_age_days"]:
        return True
    
    # Filter 3: Check posting frequency
    if account_age > 0:
        tweets_per_day = user_metrics.get('tweet_count', 0) / account_age
        if tweets_per_day > SPAM_FILTERS["max_tweets_per_day"]:
            return True
    
    # Filter 4: Check username patterns (many numbers = suspicious)
    username = user_metrics.get('username', '')
    if username:
        digit_ratio = sum(c.isdigit() for c in username) / len(username) if len(username) > 0 else 0
        if digit_ratio > 0.7:
            return True
    
    return False


def has_repeated_content(tweet_text, text_history):
    """Check if tweet content is repetitive"""
    # Normalize text
    normalized_text = re.sub(r'http\S+|@\w+', '', tweet_text)
    normalized_text = ' '.join(normalized_text.split()).lower()
    
    text_history[normalized_text] += 1
    
    # Same text appearing more than 3 times is likely spam
    return text_history[normalized_text] > 3


def scrape_tweets_api(client, search_term, start_date, end_date, text_history, collected_ids):
    """
    Scrape tweets using Twitter API v2
    Args:
        client: Tweepy client
        search_term: Search query
        start_date: Start datetime
        end_date: End datetime
        text_history: Counter for repeated content
        collected_ids: Set of previously collected IDs
    Returns:
        list: New tweet data
    """
    tweets_data = []
    
    print(f"\n📊 Scraping tweets for: {search_term}")
    
    try:
        # Format dates for API (ISO 8601 with timezone)
        start_time = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Define tweet fields to retrieve
        tweet_fields = ['created_at', 'public_metrics', 'author_id', 'lang']
        user_fields = ['username', 'name', 'public_metrics', 'created_at', 'verified']
        expansions = ['author_id']
        
        new_count = 0
        skipped_old = 0
        
        print(f"  ⏳ Searching (this may take a moment)...")
        
        # Search tweets with API v2
        response = client.search_recent_tweets(
            query=f"{search_term} lang:en -is:retweet",  # Exclude retweets
            max_results=MAX_TWEETS_PER_QUERY,
            start_time=start_time,
            end_time=end_time,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
            expansions=expansions
        )
        
        if not response.data:
            print(f"  ℹ️  No tweets found for this query")
            return tweets_data
        
        # Create user lookup dictionary
        users = {user.id: user for user in response.includes.get('users', [])}
        
        # Process each tweet
        for tweet in response.data:
            # Skip if already collected
            if tweet.id in collected_ids:
                skipped_old += 1
                continue
            
            # Get user information
            user = users.get(tweet.author_id)
            if not user:
                continue
            
            # Prepare user metrics for spam detection
            user_metrics = {
                'followers_count': user.public_metrics.get('followers_count', 0),
                'tweet_count': user.public_metrics.get('tweet_count', 0),
                'username': user.username
            }
            
            # Apply spam filters
            if is_spam_account(user_metrics, user.created_at):
                continue
            
            # Check for repeated content
            if has_repeated_content(tweet.text, text_history):
                continue
            
            # Extract tweet data
            tweet_data = {
                "tweet_id": tweet.id,
                "username": user.username,
                "display_name": user.name,
                "date": tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "tweet_text": tweet.text,
                "like_count": tweet.public_metrics.get('like_count', 0),
                "retweet_count": tweet.public_metrics.get('retweet_count', 0),
                "reply_count": tweet.public_metrics.get('reply_count', 0),
                "link": f"https://twitter.com/{user.username}/status/{tweet.id}",
                "search_term": search_term,
                "follower_count": user.public_metrics.get('followers_count', 0),
                "verified": user.verified if hasattr(user, 'verified') else False,
            }
            
            tweets_data.append(tweet_data)
            new_count += 1
        
        print(f"  ✓ New tweets: {new_count} | Skipped (already collected): {skipped_old}")
        
    except tweepy.errors.TooManyRequests as e:
        print(f"  ⚠️  Rate limit reached!")
        print(f"  💡 The script will wait and retry automatically...")
        print(f"  ℹ️  Consider running the script less frequently or upgrading your API tier")
        # Tweepy with wait_on_rate_limit=True will handle this automatically
        raise  # Re-raise to let tweepy handle the wait
    except tweepy.errors.Forbidden as e:
        print(f"  ❌ Access forbidden: {str(e)}")
        print(f"  💡 Check your API permissions and Bearer Token")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    
    return tweets_data


def remove_duplicates(tweets_data):
    """Remove duplicates within current collection"""
    seen_ids = set()
    unique_tweets = []
    
    for tweet in tweets_data:
        if tweet["tweet_id"] not in seen_ids:
            seen_ids.add(tweet["tweet_id"])
            unique_tweets.append(tweet)
    
    return unique_tweets


def save_data(tweets_data, format_type="csv"):
    """Save tweets to timestamped file"""
    if not tweets_data:
        print("\n⚠️  No NEW tweets to save!")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format_type == "csv":
        df = pd.DataFrame(tweets_data)
        filename = f"{OUTPUT_FILENAME}_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n💾 Data saved to {filename}")
        print(f"   Total NEW tweets: {len(df)}")
        print(f"   Average likes: {df['like_count'].mean():.2f}")
        print(f"   Average retweets: {df['retweet_count'].mean():.2f}")
        print(f"   Unique users: {df['username'].nunique()}")
    elif format_type == "json":
        filename = f"{OUTPUT_FILENAME}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tweets_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Data saved to {filename}")
        print(f"   Total NEW tweets: {len(tweets_data)}")


def append_to_master_file(tweets_data, format_type="csv"):
    """Append new tweets to master cumulative file"""
    if not tweets_data:
        return
    
    master_filename = f"{OUTPUT_FILENAME}_master.{format_type}"
    
    if format_type == "csv":
        df_new = pd.DataFrame(tweets_data)
        if os.path.exists(master_filename):
            df_new.to_csv(master_filename, mode='a', header=False, index=False, encoding='utf-8')
            print(f"✓ Appended to {master_filename}")
        else:
            df_new.to_csv(master_filename, index=False, encoding='utf-8')
            print(f"✓ Created master file: {master_filename}")
    elif format_type == "json":
        existing_data = []
        if os.path.exists(master_filename):
            with open(master_filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        existing_data.extend(tweets_data)
        with open(master_filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Updated master file (Total: {len(existing_data)} tweets)")


def main():
    """Main execution function"""
    print("="*60)
    print("🚀 Crypto Tweet Scraper - Twitter API v2")
    print("="*60)
    print(f"ℹ️  Collecting tweets from the last {SEARCH_DAYS} days")
    print("   (Free tier limit - upgrade to Academic for 30 days)")
    print(f"\n⚡ Optimized queries: {len(SEARCH_TERMS)} combined searches")
    print("   (Fewer queries = faster collection & less rate limiting)")
    
    # Initialize Twitter client
    client = initialize_twitter_client()
    
    # Load tracking data
    collected_ids = load_collected_tweet_ids()
    
    # Calculate date range
    start_date, end_date = calculate_date_range()
    print(f"\n📅 Date range: {start_date.date()} to {end_date.date()}")
    
    # Initialize text tracking
    text_history = Counter()
    all_tweets = []
    
    # Collect tweets for each search term
    for i, search_term in enumerate(SEARCH_TERMS, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(SEARCH_TERMS)}] Processing query...")
        print(f"{'='*60}")
        tweets = scrape_tweets_api(client, search_term, start_date, end_date, text_history, collected_ids)
        all_tweets.extend(tweets)
        
        # Rate limit friendly delay between queries
        if i < len(SEARCH_TERMS):
            print(f"\n⏸️  Waiting 3 seconds before next query...")
            time.sleep(3)
    
    # Remove duplicates
    print(f"\n🔍 Removing duplicates...")
    unique_tweets = remove_duplicates(all_tweets)
    print(f"   Before: {len(all_tweets)} | After: {len(unique_tweets)}")
    
    if unique_tweets:
        # Update tracking
        new_ids = {tweet["tweet_id"] for tweet in unique_tweets}
        collected_ids.update(new_ids)
        save_collected_tweet_ids(collected_ids)
        
        # Save data
        save_data(unique_tweets, format_type=OUTPUT_FORMAT)
        append_to_master_file(unique_tweets, format_type=OUTPUT_FORMAT)
    else:
        print("\n⚠️  No new tweets found!")
        print("   • All recent tweets already collected, or")
        print("   • No tweets match your criteria")
        print("   • Try again later for fresh content")
    
    print("\n" + "="*60)
    print("✅ Collection Complete!")
    print(f"📊 Total unique tweets tracked: {len(collected_ids)}")
    print("="*60)


if __name__ == "__main__":
    main()