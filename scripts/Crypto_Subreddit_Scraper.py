import praw
import os
import json
import csv
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

try:
    from dotenv import load_dotenv
except Exception:
    # Minimal fallback for load_dotenv if python-dotenv is not installed.
    def load_dotenv(dotenv_path=None, override=False):
        """
        Very small .env loader: reads KEY=VALUE lines from a .env file and sets os.environ.
        - dotenv_path: path to .env file (defaults to './.env')
        - override: if True, existing environment variables are overwritten
        """
        path = dotenv_path or ".env"
        try:
            with open(path, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if override or (key not in os.environ):
                        os.environ[key] = val
        except FileNotFoundError:
            # No .env file found; silently continue (matches behavior of python-dotenv)
            pass

class CryptoRedditScraper:
    def __init__(self, client_id, client_secret, user_agent, username=None, password=None):
        """
        Initialize the Reddit scraper with PRAW credentials.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string (e.g., "CryptoScraper/1.0")
            username: Reddit username (optional, for authenticated requests)
            password: Reddit password (optional, for authenticated requests)
        """
        # Initialize with or without username/password
        if username and password:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                username=username,
                password=password
            )
            print("✅ Authenticated mode (with username/password)")
        else:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            print("✅ Read-only mode (no username/password needed for scraping)")
        
        self.target_subreddits = ['cryptocurrency', 'bitcoin', 'ethereum', 'solana']
        self.posts_data = []
        self.comments_data = []
        
    def scrape_subreddit_posts(self, subreddit_name, time_filter='month', limit=100):
        """
        Scrape top posts from a subreddit for the last 30 days.
        
        Args:
            subreddit_name: Name of the subreddit
            time_filter: Time filter (day/week/month/year/all)
            limit: Maximum number of posts to scrape
        """
        print(f"\nScraping r/{subreddit_name}...")
        subreddit = self.reddit.subreddit(subreddit_name)
        
        try:
            for post in subreddit.top(time_filter=time_filter, limit=limit):
                post_data = {
                    'subreddit': subreddit_name,
                    'post_id': post.id,
                    'title': post.title,
                    'author': str(post.author) if post.author else '[deleted]',
                    'created_utc': datetime.fromtimestamp(post.created_utc).isoformat(),
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'url': post.url,
                    'permalink': f"https://reddit.com{post.permalink}",
                    'selftext': post.selftext,
                    'link_flair_text': post.link_flair_text,
                    'is_self': post.is_self,
                    'distinguished': post.distinguished,
                    'stickied': post.stickied
                }
                
                self.posts_data.append(post_data)
                print(f"  - Collected: {post.title[:50]}... (Score: {post.score})")
                
        except Exception as e:
            print(f"Error scraping r/{subreddit_name}: {e}")
    
    def scrape_post_comments(self, post_id, subreddit_name, max_comments=200):
        """
        Scrape comments from a specific post.
        
        Args:
            post_id: Reddit post ID
            subreddit_name: Name of the subreddit
            max_comments: Maximum number of comments to collect
        """
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Remove "MoreComments" objects
            
            comment_count = 0
            for comment in submission.comments.list()[:max_comments]:
                if comment_count >= max_comments:
                    break
                    
                comment_data = {
                    'post_id': post_id,
                    'subreddit': subreddit_name,
                    'comment_id': comment.id,
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat(),
                    'body': comment.body,
                    'score': comment.score,
                    'is_submitter': comment.is_submitter,
                    'distinguished': comment.distinguished,
                    'parent_id': comment.parent_id,
                    'depth': comment.depth
                }
                
                self.comments_data.append(comment_data)
                comment_count += 1
                
        except Exception as e:
            print(f"Error scraping comments for post {post_id}: {e}")
    
    def scrape_all_subreddits(self, posts_per_subreddit=100, comments_per_post=50):
        """
        Scrape posts from all target subreddits and their comments.
        
        Args:
            posts_per_subreddit: Number of posts to scrape per subreddit
            comments_per_post: Number of comments to scrape per post
        """
        print("="*60)
        print("Starting Cryptocurrency Subreddit Scraping")
        print("="*60)
        
        # Scrape posts from all subreddits
        for subreddit in self.target_subreddits:
            self.scrape_subreddit_posts(subreddit, time_filter='month', limit=posts_per_subreddit)
            time.sleep(2)  # Rate limiting
        
        print(f"\nTotal posts collected: {len(self.posts_data)}")
        
        # Scrape comments from popular posts (top 20% by score)
        print("\nScraping comments from popular posts...")
        sorted_posts = sorted(self.posts_data, key=lambda x: x['score'], reverse=True)
        top_posts = sorted_posts[:int(len(sorted_posts) * 0.2)]
        
        for i, post in enumerate(top_posts):
            print(f"Scraping comments {i+1}/{len(top_posts)}: {post['title'][:50]}...")
            self.scrape_post_comments(post['post_id'], post['subreddit'], max_comments=comments_per_post)
            time.sleep(2)  # Rate limiting
        
        print(f"\nTotal comments collected: {len(self.comments_data)}")
    
    def save_to_json(self, output_dir='data/raw'):
        """Save scraped data to JSON files."""
        # Create directories
        posts_dir = os.path.join(output_dir, 'posts')
        comments_dir = os.path.join(output_dir, 'comments')
        os.makedirs(posts_dir, exist_ok=True)
        os.makedirs(comments_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save posts
        posts_file = os.path.join(posts_dir, f'crypto_posts_{timestamp}.json')
        with open(posts_file, 'w', encoding='utf-8') as f:
            json.dump(self.posts_data, f, indent=2, ensure_ascii=False)
        print(f"\nPosts saved to: {posts_file}")
        
        # Save comments
        comments_file = os.path.join(comments_dir, f'crypto_comments_{timestamp}.json')
        with open(comments_file, 'w', encoding='utf-8') as f:
            json.dump(self.comments_data, f, indent=2, ensure_ascii=False)
        print(f"Comments saved to: {comments_file}")
    
    def save_to_csv(self, output_dir='data/raw'):
        """Save scraped data to CSV files."""
        # Create directories
        posts_dir = os.path.join(output_dir, 'posts')
        comments_dir = os.path.join(output_dir, 'comments')
        os.makedirs(posts_dir, exist_ok=True)
        os.makedirs(comments_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save posts
        if self.posts_data:
            posts_file = os.path.join(posts_dir, f'crypto_posts_{timestamp}.csv')
            with open(posts_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.posts_data[0].keys())
                writer.writeheader()
                writer.writerows(self.posts_data)
            print(f"Posts CSV saved to: {posts_file}")
        
        # Save comments
        if self.comments_data:
            comments_file = os.path.join(comments_dir, f'crypto_comments_{timestamp}.csv')
            with open(comments_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.comments_data[0].keys())
                writer.writeheader()
                writer.writerows(self.comments_data)
            print(f"Comments CSV saved to: {comments_file}")
    
    def get_statistics(self):
        """Print statistics about the scraped data."""
        print("\n" + "="*60)
        print("SCRAPING STATISTICS")
        print("="*60)
        
        print(f"\nTotal Posts: {len(self.posts_data)}")
        print(f"Total Comments: {len(self.comments_data)}")
        
        # Posts by subreddit
        print("\nPosts by Subreddit:")
        for subreddit in self.target_subreddits:
            count = sum(1 for post in self.posts_data if post['subreddit'] == subreddit)
            print(f"  r/{subreddit}: {count}")
        
        # Average scores
        if self.posts_data:
            avg_post_score = sum(post['score'] for post in self.posts_data) / len(self.posts_data)
            print(f"\nAverage Post Score: {avg_post_score:.2f}")
        
        if self.comments_data:
            avg_comment_score = sum(comment['score'] for comment in self.comments_data) / len(self.comments_data)
            print(f"Average Comment Score: {avg_comment_score:.2f}")


def main():
    """
    Main function to run the scraper using environment variables.
    
    SETUP INSTRUCTIONS:
    1. Install required packages:
       pip install praw python-dotenv
    
    2. Create a .env file in the same directory as this script
    
    3. Get Reddit API credentials:
       - Go to https://www.reddit.com/prefs/apps
       - Click "Create App" or "Create Another App"
       - Select "script" as app type
       - Fill in the required information
       - Copy client ID and secret to .env file
    
    4. Run the script:
       python crypto_scraper.py
    """
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials from environment variables
    CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    USER_AGENT = os.getenv('REDDIT_USER_AGENT')
    USERNAME = os.getenv('REDDIT_USERNAME')  # Optional
    PASSWORD = os.getenv('REDDIT_PASSWORD')  # Optional
    
    # Get optional configuration
    POSTS_PER_SUBREDDIT = int(os.getenv('POSTS_PER_SUBREDDIT', 100))
    COMMENTS_PER_POST = int(os.getenv('COMMENTS_PER_POST', 50))
    OUTPUT_DIR = os.getenv('OUTPUT_DIRECTORY', 'output')
    
    # Validate credentials
    if not all([CLIENT_ID, CLIENT_SECRET, USER_AGENT]):
        print("ERROR: Missing required environment variables!")
        print("Please check your .env file and ensure it contains:")
        print("  - REDDIT_CLIENT_ID")
        print("  - REDDIT_CLIENT_SECRET")
        print("  - REDDIT_USER_AGENT")
        return
    
    print("Loading credentials from .env file...")
    print(f"Client ID: {CLIENT_ID[:8]}... (length: {len(CLIENT_ID)})")
    print(f"Client Secret: {CLIENT_SECRET[:8]}... (length: {len(CLIENT_SECRET)})")
    print(f"User Agent: {USER_AGENT}")
    print(f"Posts per subreddit: {POSTS_PER_SUBREDDIT}")
    print(f"Comments per post: {COMMENTS_PER_POST}")
    
    # Test connection first
    print("\nTesting Reddit API connection...")
    try:
        test_reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT
        )
        # Try to access a subreddit to verify credentials
        test_sub = test_reddit.subreddit('cryptocurrency')
        test_post = next(test_sub.hot(limit=1))
        print(f"✅ Connection successful! Retrieved test post: '{test_post.title[:50]}...'")
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nPlease check:")
        print("1. Client ID and Secret are copied correctly (no extra spaces)")
        print("2. Your Reddit app type is 'script' not 'web app'")
        print("3. Go to https://www.reddit.com/prefs/apps to verify")
        return
    
    # Initialize scraper
    scraper = CryptoRedditScraper(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        username=USERNAME,  # Optional
        password=PASSWORD   # Optional
    )
    
    # Scrape data
    scraper.scrape_all_subreddits(
        posts_per_subreddit=POSTS_PER_SUBREDDIT,
        comments_per_post=COMMENTS_PER_POST
    )
    
    # Display statistics
    scraper.get_statistics()
    
    # Save data
    scraper.save_to_json(output_dir=OUTPUT_DIR)
    scraper.save_to_csv(output_dir=OUTPUT_DIR)
    
    print("\n" + "="*60)
    print("Scraping completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()