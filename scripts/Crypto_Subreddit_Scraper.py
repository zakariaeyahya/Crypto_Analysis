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
    def load_dotenv(dotenv_path=None, override=False):
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
            pass

class CryptoRedditScraper:
    def __init__(self, client_id, client_secret, user_agent, username=None, password=None, output_dir='data/raw'):
        """
        Initialize the Reddit scraper with PRAW credentials.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string (e.g., "CryptoScraper/1.0")
            username: Reddit username (optional, for authenticated requests)
            password: Reddit password (optional, for authenticated requests)
            output_dir: Directory for saving data and state
        """
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
        self.output_dir = output_dir
        self.state_file = os.path.join(output_dir, 'scraper_state.json')
        
        # Load previous state
        self.last_scrape_time = self._load_last_scrape_time()
        self.scraped_post_ids = self._load_scraped_post_ids()
        
    def _load_last_scrape_time(self):
        """Load the timestamp of the last scrape."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    last_time = state.get('last_scrape_time')
                    if last_time:
                        dt = datetime.fromisoformat(last_time)
                        print(f"📅 Last scrape: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        return dt
            except Exception as e:
                print(f"⚠️ Could not load last scrape time: {e}")
        
        # If no previous scrape, default to 30 days ago
        default_time = datetime.now() - timedelta(days=30)
        print(f"📅 No previous scrape found. Will collect posts from last 30 days.")
        return default_time
    
    def _load_scraped_post_ids(self):
        """Load previously scraped post IDs to avoid duplicates."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    post_ids = set(state.get('scraped_post_ids', []))
                    if post_ids:
                        print(f"📋 Found {len(post_ids)} previously scraped posts")
                    return post_ids
            except Exception as e:
                print(f"⚠️ Could not load scraped post IDs: {e}")
        return set()
    
    def _save_state(self):
        """Save the current scraping state."""
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Add new post IDs to the set
        new_post_ids = {post['post_id'] for post in self.posts_data}
        self.scraped_post_ids.update(new_post_ids)
        
        state = {
            'last_scrape_time': datetime.now().isoformat(),
            'scraped_post_ids': list(self.scraped_post_ids),
            'total_posts_scraped': len(self.scraped_post_ids),
            'last_run_stats': {
                'new_posts': len(self.posts_data),
                'new_comments': len(self.comments_data)
            }
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"\n💾 State saved: {len(new_post_ids)} new posts tracked")
        
    def scrape_subreddit_posts(self, subreddit_name, limit=500):
        """
        Scrape new posts from a subreddit since last run.
        
        Args:
            subreddit_name: Name of the subreddit
            limit: Maximum number of posts to check (checks newest first)
        """
        print(f"\n🔍 Scraping r/{subreddit_name}...")
        subreddit = self.reddit.subreddit(subreddit_name)
        
        new_posts_count = 0
        skipped_count = 0
        
        try:
            # Use 'new' to get most recent posts
            for post in subreddit.new(limit=limit):
                post_time = datetime.fromtimestamp(post.created_utc)
                
                # Skip if post is older than last scrape
                if post_time <= self.last_scrape_time:
                    continue
                
                # Skip if we've already scraped this post
                if post.id in self.scraped_post_ids:
                    skipped_count += 1
                    continue
                
                post_data = {
                    'subreddit': subreddit_name,
                    'post_id': post.id,
                    'title': post.title,
                    'author': str(post.author) if post.author else '[deleted]',
                    'created_utc': post_time.isoformat(),
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
                new_posts_count += 1
                print(f"  ✅ New: {post.title[:60]}... (Score: {post.score})")
                
        except Exception as e:
            print(f"❌ Error scraping r/{subreddit_name}: {e}")
        
        print(f"  📊 Found {new_posts_count} new posts, skipped {skipped_count} duplicates")
    
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
            submission.comments.replace_more(limit=0)
            
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
            print(f"❌ Error scraping comments for post {post_id}: {e}")
    
    def scrape_all_subreddits(self, posts_limit=500, comments_per_post=50):
        """
        Scrape new posts from all target subreddits and their comments.
        
        Args:
            posts_limit: Number of recent posts to check per subreddit
            comments_per_post: Number of comments to scrape per post
        """
        print("="*60)
        print("🚀 Starting Incremental Cryptocurrency Scraping")
        print("="*60)
        
        # Scrape posts from all subreddits
        for subreddit in self.target_subreddits:
            self.scrape_subreddit_posts(subreddit, limit=posts_limit)
            time.sleep(2)  # Rate limiting
        
        print(f"\n📈 Total NEW posts collected: {len(self.posts_data)}")
        
        if len(self.posts_data) == 0:
            print("✨ No new posts found since last scrape!")
            return
        
        # Scrape comments from popular new posts (top 30% by score)
        print("\n💬 Scraping comments from popular new posts...")
        sorted_posts = sorted(self.posts_data, key=lambda x: x['score'], reverse=True)
        top_posts = sorted_posts[:max(1, int(len(sorted_posts) * 0.3))]
        
        for i, post in enumerate(top_posts):
            print(f"  {i+1}/{len(top_posts)}: {post['title'][:50]}...")
            self.scrape_post_comments(post['post_id'], post['subreddit'], max_comments=comments_per_post)
            time.sleep(2)  # Rate limiting
        
        print(f"\n📈 Total NEW comments collected: {len(self.comments_data)}")
    
    def save_to_json(self):
        """Save scraped data to JSON files."""
        if not self.posts_data and not self.comments_data:
            print("\n⚠️ No new data to save.")
            return
            
        posts_dir = os.path.join(self.output_dir, 'posts')
        comments_dir = os.path.join(self.output_dir, 'comments')
        os.makedirs(posts_dir, exist_ok=True)
        os.makedirs(comments_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save posts
        if self.posts_data:
            posts_file = os.path.join(posts_dir, f'crypto_posts_{timestamp}.json')
            with open(posts_file, 'w', encoding='utf-8') as f:
                json.dump(self.posts_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Posts saved to: {posts_file}")
        
        # Save comments
        if self.comments_data:
            comments_file = os.path.join(comments_dir, f'crypto_comments_{timestamp}.json')
            with open(comments_file, 'w', encoding='utf-8') as f:
                json.dump(self.comments_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Comments saved to: {comments_file}")
    
    def save_to_csv(self):
        """Save scraped data to CSV files."""
        if not self.posts_data and not self.comments_data:
            return
            
        posts_dir = os.path.join(self.output_dir, 'posts')
        comments_dir = os.path.join(self.output_dir, 'comments')
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
            print(f"💾 Posts CSV saved to: {posts_file}")
        
        # Save comments
        if self.comments_data:
            comments_file = os.path.join(comments_dir, f'crypto_comments_{timestamp}.csv')
            with open(comments_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.comments_data[0].keys())
                writer.writeheader()
                writer.writerows(self.comments_data)
            print(f"💾 Comments CSV saved to: {comments_file}")
    
    def get_statistics(self):
        """Print statistics about the scraped data."""
        print("\n" + "="*60)
        print("📊 SCRAPING STATISTICS")
        print("="*60)
        
        print(f"\n✨ NEW Posts This Run: {len(self.posts_data)}")
        print(f"✨ NEW Comments This Run: {len(self.comments_data)}")
        print(f"📚 Total Posts Ever Scraped: {len(self.scraped_post_ids) + len(self.posts_data)}")
        
        # Posts by subreddit
        if self.posts_data:
            print("\n📍 New Posts by Subreddit:")
            for subreddit in self.target_subreddits:
                count = sum(1 for post in self.posts_data if post['subreddit'] == subreddit)
                if count > 0:
                    print(f"  r/{subreddit}: {count}")
            
            # Average scores
            avg_post_score = sum(post['score'] for post in self.posts_data) / len(self.posts_data)
            print(f"\n⭐ Average Post Score: {avg_post_score:.2f}")
        
        if self.comments_data:
            avg_comment_score = sum(comment['score'] for comment in self.comments_data) / len(self.comments_data)
            print(f"⭐ Average Comment Score: {avg_comment_score:.2f}")


def main():
    """
    Main function to run the incremental scraper.
    
    SETUP INSTRUCTIONS:
    1. Install required packages:
       pip install praw python-dotenv
    
    2. Create a .env file with your Reddit API credentials
    
    3. Run daily/hourly to collect only new data since last run:
       python crypto_scraper.py
    
    The scraper will automatically:
    - Track the last scrape time
    - Only collect posts created since then
    - Skip duplicate posts
    - Save incremental data files
    """
    
    load_dotenv()
    
    CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    USER_AGENT = os.getenv('REDDIT_USER_AGENT')
    USERNAME = os.getenv('REDDIT_USERNAME')
    PASSWORD = os.getenv('REDDIT_PASSWORD')
    
    POSTS_LIMIT = int(os.getenv('POSTS_LIMIT', 500))  # Check more recent posts
    COMMENTS_PER_POST = int(os.getenv('COMMENTS_PER_POST', 50))
    OUTPUT_DIR = os.getenv('OUTPUT_DIRECTORY', 'output')
    
    if not all([CLIENT_ID, CLIENT_SECRET, USER_AGENT]):
        print("❌ ERROR: Missing required environment variables!")
        print("Please check your .env file.")
        return
    
    print("🔐 Loading credentials from .env file...")
    print(f"Client ID: {CLIENT_ID[:8]}...")
    print(f"User Agent: {USER_AGENT}")
    
    # Test connection
    print("\n🔌 Testing Reddit API connection...")
    try:
        test_reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT
        )
        test_sub = test_reddit.subreddit('cryptocurrency')
        test_post = next(test_sub.hot(limit=1))
        print(f"✅ Connection successful!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Initialize scraper
    scraper = CryptoRedditScraper(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        username=USERNAME,
        password=PASSWORD,
        output_dir=OUTPUT_DIR
    )
    
    # Scrape data
    scraper.scrape_all_subreddits(
        posts_limit=POSTS_LIMIT,
        comments_per_post=COMMENTS_PER_POST
    )
    
    # Display statistics
    scraper.get_statistics()
    
    # Save data and state
    scraper.save_to_json()
    scraper.save_to_csv()
    scraper._save_state()  # Save state for next run
    
    print("\n" + "="*60)
    print("✅ Scraping completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()