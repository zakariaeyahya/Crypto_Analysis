# Crypto Reddit Scraper 🚀

A Python-based tool for scraping posts and comments from cryptocurrency-related subreddits using the Reddit API (PRAW). Perfect for sentiment analysis, trend detection, and market research.
## 🧠 Project Progress

### 🗓️ Updates Log

- **30/10/2025** — Added new scraping run results (see details below).

============================================================
✨ NEW Posts This Run: 1533
✨ NEW Comments This Run: 13775
📚 Total Posts Ever Scraped: 1533

📍 New Posts by Subreddit:
  r/cryptocurrency: 500
  r/bitcoin: 500
  r/ethereum: 113
  r/solana: 420

⭐ Average Post Score: 108.37
⭐ Average Comment Score: 9.32

💾 Posts saved to: output\posts\crypto_posts_20251030_140452.json
💾 Comments saved to: output\comments\crypto_comments_20251030_140452.json
💾 Posts CSV saved to: output\posts\crypto_posts_20251030_140459.csv
💾 Comments CSV saved to: output\comments\crypto_comments_20251030_140459.csv

💾 State saved: 1533 new posts tracked
============================================================
✅ Scraping completed successfully!
============================================================


- **October 29, 2025**

| Metric | Value |
|--------|-------|
| **Total Posts** | 831 |
| **Total Comments** | 12,752 |
| **Average Post Score** | 630.52 |
| **Average Comment Score** | 16.54 |

### Posts by Subreddit
- **r/cryptocurrency**: 242 posts
- **r/bitcoin**: 242 posts
- **r/solana**: 233 posts
- **r/ethereum**: 114 posts

## 🎯 Features

- ✅ Scrapes top posts from the last 30 days
- ✅ Collects comments from popular threads
- ✅ Supports multiple cryptocurrency subreddits
- ✅ Exports data in both JSON and CSV formats
- ✅ Built-in rate limiting to respect Reddit API
- ✅ Detailed logging and statistics
- ✅ Secure credential management with `.env`
- ✅ Organized data structure for easy analysis

## 📊 Data Format
### Posts Data

Each post contains:
- `subreddit` - Subreddit name
- `post_id` - Unique post identifier
- `title` - Post title
- `author` - Post author username
- `created_utc` - Timestamp (ISO format)
- `score` - Upvotes minus downvotes
- `upvote_ratio` - Ratio of upvotes
- `num_comments` - Number of comments
- `url` - Post URL
- `permalink` - Reddit permalink
- `selftext` - Post text content
- `link_flair_text` - Post flair
- `is_self` - Is it a self post?
- `distinguished` - Moderator/admin status
- `stickied` - Is post stickied?

### Comments Data

Each comment contains:
- `post_id` - Parent post ID
- `subreddit` - Subreddit name
- `comment_id` - Unique comment identifier
- `author` - Comment author username
- `created_utc` - Timestamp (ISO format)
- `body` - Comment text
- `score` - Comment score
- `is_submitter` - Is author the OP?
- `distinguished` - Moderator/admin status
- `parent_id` - Parent comment/post ID
- `depth` - Comment depth in thread

