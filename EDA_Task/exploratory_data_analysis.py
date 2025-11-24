"""
Comprehensive Dataset Overview and Cryptocurrency Extraction
Modified to save plots instead of showing them
"""

import logging
from pathlib import Path
import pandas as pd
from collections import Counter
from typing import List
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for Docker
import matplotlib.pyplot as plt

# === Logging configuration ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# === Create plots directory ===
PLOTS_DIR = Path("plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
logger.info(f"Plots will be saved to: {PLOTS_DIR.absolute()}")

# === 1. Load dataset ===
DATA_PATH = Path("master_dataset.csv")
if not DATA_PATH.exists():
    logger.error(f"Dataset not found at {DATA_PATH}")
    exit(1)

df = pd.read_csv(DATA_PATH)
logger.info(f"Dataset loaded with {len(df)} rows")

# === 2. Identify posts and comments based on 'unified_id' ===
def classify_post_type(unified_id: str) -> str:
    if unified_id.startswith("p_"):
        return "post"
    elif unified_id.startswith("c_"):
        return "comment"
    return "unknown"

df["type"] = df["unified_id"].astype(str).apply(classify_post_type)

# === 3. Compute counts ===
total_posts = (df["type"] == "post").sum()
total_comments = (df["type"] == "comment").sum()
distinct_posts = df.loc[df["type"] == "post", "unified_id"].nunique()
distinct_comments = df.loc[df["type"] == "comment", "unified_id"].nunique()

# === 4. Convert 'created_date' to datetime ===
df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
date_min = df["created_date"].min()
date_max = df["created_date"].max()

# === 5. Count sources if available ===
source_counts = df.get("source_platform", pd.Series()).value_counts().to_dict()
if not source_counts:
    source_counts = {"Info": "No 'source_platform' column found"}

# === 6. Extract unique cryptocurrencies from 'subreddit' ===
def extract_cryptos(column: pd.Series) -> list:
    return (
        column.dropna()
        .astype(str)
        .str.lower()
        .str.split(",")
        .explode()
        .str.strip()
        .loc[lambda x: x != ""]
        .unique()
        .tolist()
    )

crypto_unique = extract_cryptos(df["subreddit"]) if "subreddit" in df.columns else []

# === 7. Count distinct authors ===
nb_authors = df["author"].nunique()

# === 8. Log results ===
logger.info("=== Dataset Statistics ===")
logger.info(f"Total posts: {total_posts}")
logger.info(f"Total comments: {total_comments}")
logger.info(f"Distinct posts: {distinct_posts}")
logger.info(f"Distinct comments: {distinct_comments}")
logger.info(f"Time period: from {date_min} to {date_max}")
logger.info(f"Sources: {source_counts}")
logger.info(f"Number of distinct authors: {nb_authors}")

logger.info("=== Cryptocurrencies extracted from 'subreddit' ===")
logger.info(f"Number of distinct cryptos: {len(crypto_unique)}")
logger.info(f"Cryptos: {crypto_unique}")

# === Cryptocurrency Frequency Analysis from Subreddit Column ===

# === 9. Extract and count cryptocurrencies from 'subreddit' ===
def extract_cryptos_list(subreddit_column: pd.Series) -> List[str]:
    """Extracts and normalizes cryptocurrency names from a pandas Series."""
    all_cryptos = []
    for cell in subreddit_column.dropna():
        items = [c.strip().lower() for c in str(cell).split(",") if c.strip()]
        all_cryptos.extend(items)
    return all_cryptos

if "subreddit" in df.columns:
    all_cryptos = extract_cryptos_list(df["subreddit"])
    crypto_counts = Counter(all_cryptos)

    crypto_freq_df = (
        pd.DataFrame(crypto_counts.items(), columns=["crypto", "count"])
        .sort_values(by="count", ascending=False)
        .reset_index(drop=True)
    )

    logger.info("=== Top 20 Cryptocurrencies by Frequency ===")
    logger.info(f"\n{crypto_freq_df.head(20)}")
else:
    logger.info("No 'subreddit' column found. Skipping cryptocurrency frequency analysis.")

# === Text Content Length Analysis ===

# === 10. Text Length Analysis ===
if "text_content" in df.columns:
    # Compute the length of each text entry
    df["text_length"] = df["text_content"].astype(str).apply(len)

    # Compute basic statistics
    text_min = df["text_length"].min()
    text_max = df["text_length"].max()
    text_mean = df["text_length"].mean()
    text_var = df["text_length"].var()

    # Log results
    logger.info("=== Text Length Statistics ===")
    logger.info(f"Minimum text length: {text_min}")
    logger.info(f"Maximum text length: {text_max}")
    logger.info(f"Mean text length: {text_mean:.2f}")
    logger.info(f"Variance of text lengths: {text_var:.2f}")
else:
    logger.info("Column 'text_content' not found in the dataset. Skipping text length analysis.")

# === Percentage Distribution of Posts and Comments ===

# === 11. Distribution (%) of Posts and Comments ===
if "type" in df.columns:
    # Compute percentage distribution
    type_counts = df["type"].value_counts(normalize=True) * 100

    # Log the distribution
    logger.info("=== Percentage Distribution of Posts and Comments ===")
    logger.info(f"\n{type_counts}")

    # Create a pie chart
    plt.figure(figsize=(4, 4))
    plt.pie(
        type_counts,
        labels=None,  # Do not put labels directly on the pie
        autopct="%1.1f%%",
        startangle=90,
        colors=["skyblue", "lightgreen"],
        wedgeprops={"edgecolor": "black"}
    )
    plt.title("Distribution (%) of Posts and Comments")

    # Add a legend to the right
    plt.legend(
        labels=type_counts.index,
        title="Content Type",
        loc="center left",
        bbox_to_anchor=(1, 0.5)  # Position legend to the right
    )

    plt.tight_layout()

    # Save plot instead of showing
    plot_path = PLOTS_DIR / "01_posts_comments_distribution.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"✅ Saved plot: {plot_path}")
else:
    logger.info("Column 'type' not found in the dataset. Skipping posts/comments distribution chart.")

# === Top 7 Most Mentioned Cryptocurrencies ===

# === 12. Top 7 Most Mentioned Cryptocurrencies (Posts + Comments) ===
if "crypto_freq_df" in globals() and not crypto_freq_df.empty:
    top7 = crypto_freq_df.head(7)

    # Log the top 7
    logger.info("=== Top 7 Most Mentioned Cryptocurrencies ===")
    logger.info(f"\n{top7}")

    # Create horizontal bar chart
    plt.figure(figsize=(5, 3))
    plt.barh(
        top7["crypto"],
        top7["count"],
        color="skyblue",
        edgecolor="black",
        height=0.5  # thinner bars
    )

    plt.title("Top 7 Most Mentioned Cryptos (Posts + Comments)")
    plt.xlabel("Number of Occurrences")
    plt.ylabel("Cryptocurrency")
    plt.gca().invert_yaxis()  # Most mentioned on top

    plt.tight_layout()

    # Save plot instead of showing
    plot_path = PLOTS_DIR / "02_top7_cryptos.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"✅ Saved plot: {plot_path}")
else:
    logger.info("Crypto frequency DataFrame is empty or not defined. Skipping top 7 chart.")

# === Daily Trends of Posts and Comments ===

# === Identify posts and comments ===
if "unified_id" in df.columns:
    df["type"] = df["unified_id"].astype(str).apply(
        lambda x: "post" if x.startswith("p_") else ("comment" if x.startswith("c_") else "unknown")
    )
else:
    df["type"] = "unknown"
    logger.info("Column 'unified_id' not found. All entries set as 'unknown'.")

# === Extract date ===
if "created_date" in df.columns:
    df["date"] = pd.to_datetime(df["created_date"], errors="coerce").dt.date
else:
    df["date"] = pd.NaT
    logger.info("Column 'created_date' not found. Daily plot may be empty.")

# === Count entries per day and type ===
counts_per_day = df.groupby(["date", "type"]).size().unstack(fill_value=0)
counts_per_day["total"] = counts_per_day.sum(axis=1)

logger.info("=== Daily Counts of Posts and Comments ===")
logger.info(f"\n{counts_per_day.head()}")  # Preview first few rows

# === Plot daily trends ===
plt.figure(figsize=(12, 6))
plt.plot(counts_per_day.index, counts_per_day["total"], label="Total", linestyle="-", color="black")
plt.plot(counts_per_day.index, counts_per_day.get("post", 0), label="Posts", linestyle="--", color="lightgreen")
plt.plot(counts_per_day.index, counts_per_day.get("comment", 0), label="Comments", linestyle=":", color="skyblue")

plt.title("Daily Evolution of Posts and Comments")
plt.xlabel("Date")
plt.ylabel("Number of Entries")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

# Save plot instead of showing
plot_path = PLOTS_DIR / "03_daily_trends.png"
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
plt.close()
logger.info(f"✅ Saved plot: {plot_path}")

# === Posts and Comments Distribution by Cryptocurrency (Top 10) ===

# === Distribution of posts and comments by cryptocurrency ===
if "subreddit" in df.columns and "type" in df.columns:
    # Explode the subreddit column to have one row per crypto
    df_exploded = (
        df.dropna(subset=["subreddit"])
        .assign(subreddit=df["subreddit"].str.lower().str.split(","))
        .explode("subreddit")
    )
    df_exploded["subreddit"] = df_exploded["subreddit"].str.strip()

    # Group by crypto and type
    crypto_type_counts = (
        df_exploded.groupby(["subreddit", "type"])
        .size()
        .unstack(fill_value=0)
        .sort_values(by="comment", ascending=False)
    )

    # Top 10 most active cryptos
    top_cryptos = crypto_type_counts.head(10)

    logger.info("=== Top 10 Cryptocurrencies by Posts and Comments ===")
    logger.info(f"\n{top_cryptos}")

    # === Stacked bar chart ===
    top_cryptos.plot(
        kind="bar",
        stacked=True,
        color=["skyblue", "lightgreen"],
        edgecolor="black",
        figsize=(10, 6)
    )

    plt.title("Posts and Comments Distribution by Crypto (Top 10)")
    plt.xlabel("Cryptocurrency")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.legend(title="Type")
    plt.tight_layout()

    # Save plot instead of showing
    plot_path = PLOTS_DIR / "04_crypto_distribution_top10.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"✅ Saved plot: {plot_path}")
else:
    logger.info("Columns 'subreddit' and/or 'type' not found in the dataset. Skipping crypto distribution chart.")

# === Summary ===
logger.info("=" * 60)
logger.info("EDA COMPLETED - All plots saved successfully")
logger.info(f"Plots directory: {PLOTS_DIR.absolute()}")
logger.info("=" * 60)

