import json
import pandas as pd
import os
import logging
from scipy.stats import pearsonr

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_PATH, "data")

SENTIMENT_PATH = os.path.join(
    DATA_PATH, "gold", "sentiment_timeseries.json"
)

ENRICHED_PATH = os.path.join(
    DATA_PATH, "silver", "enriched_data", "crypto_sent_enriched_price.json"
)

OUTPUT_JSON = os.path.join(
    DATA_PATH, "gold", "sentiment_price_correlation.json"
)

# LOAD DATA

with open(SENTIMENT_PATH, "r", encoding="utf-8") as f:
    sentiment_data = json.load(f)

with open(ENRICHED_PATH, "r", encoding="utf-8") as f:
    price_data = json.load(f)

df_sent = pd.DataFrame(sentiment_data)
df_price = pd.DataFrame(price_data)

logging.info(f"Loaded {len(df_sent)} sentiment rows")
logging.info(f"Loaded {len(df_price)} price rows")

# PREPARE DATA 

# Normalize sentiment dates to YYYY-MM-DD
df_sent["date"] = (
    pd.to_datetime(df_sent["date"], errors="coerce")
      .dt.date
)

# Normalize price dates to YYYY-MM-DD (remove time)
df_price["date"] = (
    pd.to_datetime(df_price["date"], format="mixed", errors="coerce")
      .dt.date
)

# DAILY PRICE CHANGE
df_price_daily = (
    df_price.groupby(["date", "crypto"])["price_change"]
    .mean()
    .reset_index()
)

#MERGE SENTIMENT & PRICE
df_merged = df_sent.merge(
    df_price_daily,
    on=["date", "crypto"],
    how="inner"
)

logging.info(f"Merged dataset size: {len(df_merged)}")

# CORRELATION ANALYSIS
results = []

for crypto, group in df_merged.groupby("crypto"):
    group = group.dropna(subset=["sentiment_mean", "price_change"])

    if len(group) < 3:
        logging.warning(f"Not enough data for {crypto}, skipping")
        continue

    r, p = pearsonr(group["sentiment_mean"], group["price_change"])

    results.append({
        "crypto": crypto,
        "pearson_r": float(r),
        "p_value": float(p),
        "n_observations": int(len(group))
    })


os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

logging.info(f"Output saved at: {OUTPUT_JSON}")
