"""
Twitter extraction service for cryptocurrency tweets
"""
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import tweepy

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Fix encoding for Windows console
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

logger = logging.getLogger(__name__)


class TwitterExtractor:
    """Service to extract cryptocurrency tweets from Twitter API"""
    
    def __init__(self):
        """Initialize Twitter API connection"""
        logger.info("Initializing Twitter API client...")
        
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Validate credentials
        if not all([self.api_key, self.api_secret, self.access_token, 
                   self.access_token_secret, self.bearer_token]):
            logger.error("Missing Twitter API credentials in .env file")
            raise ValueError("Twitter API credentials are missing")
        
        try:
            # Initialize API v2 client
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            logger.info("[OK] Twitter API client initialized successfully")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize Twitter API client: {e}")
            raise
    
    def extract_tweets(self, keywords: str, max_tweets: int = 100, lang: str = 'fr'):
        """
        Extract tweets based on keywords
        
        Args:
            keywords: Comma-separated keywords (e.g., "bitcoin,ethereum")
            max_tweets: Maximum number of tweets to extract
            lang: Language code (default: 'fr' for French)
        
        Returns:
            List of tweet dictionaries
        """
        # Prepare query
        keyword_list = keywords.split(",")
        query = f'({" OR ".join(keyword_list)}) lang:{lang} -is:retweet'
        
        logger.info(f"Starting tweet extraction...")
        logger.info(f"Query: {query}")
        logger.info(f"Max tweets: {max_tweets}")
        
        tweets_data = []
        start_time = datetime.now()
        
        try:
            # Search tweets
            paginator = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'text', 'lang'],
                max_results=min(max_tweets, 100)
            )
            
            for i, tweet in enumerate(paginator.flatten(limit=max_tweets), 1):
                tweets_data.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': str(tweet.created_at),
                    'author_id': tweet.author_id,
                    'lang': tweet.lang if hasattr(tweet, 'lang') else lang,
                    'metrics': tweet.public_metrics
                })
                
                # Log progress every 50 tweets
                if i % 50 == 0:
                    logger.info(f"Progress: {i}/{max_tweets} tweets extracted")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"[OK] Successfully extracted {len(tweets_data)} tweets in {duration:.2f} seconds")
            return tweets_data
            
        except tweepy.Unauthorized as e:
            logger.error(f"[ERROR] Unauthorized (401): Please check your Twitter API credentials")
            logger.error(f"[ERROR] Details: {e}")
            return []
        except tweepy.TooManyRequests:
            logger.warning("[WARN] Rate limit exceeded. Waiting...")
            return []
        except tweepy.BadRequest as e:
            logger.error(f"[ERROR] Bad request error: {e}")
            return []
        except Exception as e:
            logger.error(f"[ERROR] Error during extraction: {e}")
            return []
    
    def save_to_bronze(self, tweets: list, filename: str = "twitter_tweets"):
        """
        Save tweets to bronze layer (raw data) as CSV
        
        Args:
            tweets: List of tweet dictionaries
            filename: Base filename without extension
        """
        # Create bronze/twitter directory if it doesn't exist
        os.makedirs('data/bronze/twitter', exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f'data/bronze/twitter/{filename}_{timestamp}.csv'
        
        try:
            # Convert to DataFrame and save as CSV
            import pandas as pd
            
            # Flatten metrics if present
            for tweet in tweets:
                if 'metrics' in tweet and isinstance(tweet['metrics'], dict):
                    metrics = tweet['metrics']
                    tweet['likes'] = metrics.get('like_count', 0)
                    tweet['retweets'] = metrics.get('retweet_count', 0)
                    tweet['replies'] = metrics.get('reply_count', 0)
                    tweet['quotes'] = metrics.get('quote_count', 0)
                    del tweet['metrics']
            
            df = pd.DataFrame(tweets)
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"[OK] Saved {len(tweets)} tweets to {filepath}")
            
            # Save summary
            self._save_summary(tweets, filepath)
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to save tweets: {e}")
    
    def _save_summary(self, tweets: list, filepath: str):
        """Save extraction summary to a separate file"""
        summary = {
            'total_tweets': len(tweets),
            'extraction_date': datetime.now().isoformat(),
            'file_location': filepath,
            'average_tweet_length': sum(len(t['text']) for t in tweets) / len(tweets) if tweets else 0,
            'total_likes': sum(t['metrics'].get('like_count', 0) for t in tweets),
            'total_retweets': sum(t['metrics'].get('retweet_count', 0) for t in tweets)
        }
        
        summary_path = filepath.replace('.csv', '_summary.json')
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"📊 Summary saved to {summary_path}")
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")


def main():
    """Main function to run tweet extraction"""
    logger.info("=" * 60)
    logger.info("Starting Twitter Extraction Service")
    logger.info("=" * 60)
    
    # Load configuration from .env
    keywords = os.getenv('CRYPTO_KEYWORDS', 'bitcoin,ethereum,crypto')
    max_tweets = int(os.getenv('MAX_TWEETS', '100'))
    lang = os.getenv('TWEET_LANG', 'fr')
    
    logger.info(f"Configuration:")
    logger.info(f"  Keywords: {keywords}")
    logger.info(f"  Max tweets: {max_tweets}")
    logger.info(f"  Language: {lang}")
    
    try:
        # Initialize extractor
        extractor = TwitterExtractor()
        
        # Extract tweets
        tweets = extractor.extract_tweets(keywords, max_tweets, lang)
        
        # Save tweets
        if tweets:
            extractor.save_to_bronze(tweets, 'twitter_tweets')
            logger.info("=" * 60)
            logger.info("[OK] Extraction completed successfully")
            logger.info("=" * 60)
        else:
            logger.warning("[WARN] No tweets extracted")
            
    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()
