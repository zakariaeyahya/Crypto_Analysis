import json
import pandas as pd
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_PATH, "data")

INPUT_JSON = os.path.join(
    DATA_PATH, "silver", "enriched_data", "crypto_sent_enriched_price.json"
)

OUTPUT_JSON = os.path.join(
    DATA_PATH, "gold", "sentiment_timeseries.json"
)

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)
logging.info(f"Loaded {len(df)} rows")

# NORMALIZE CRYPTO COLUMN
if df["crypto"].apply(lambda x: isinstance(x, list)).any():
    logging.info("Exploding crypto column (list -> one crypto per row)")
    df = df.explode("crypto")

# PREPARE DATA
df["date"] = pd.to_datetime(
    df["date"],
    format="mixed",
    errors="coerce"
)

df["day"] = df["date"].dt.date


# DAILY AGGREGATION
daily_stats = (
    df.groupby(["day", "crypto"])["sentiment_score"]
      .agg(sentiment_mean="mean", sentiment_std="std")
      .reset_index()
)

sentiment_counts = (
    df.groupby(["day", "crypto", "sentiment"])
      .size()
      .unstack(fill_value=0)
      .reset_index()
)

df_daily = daily_stats.merge(
    sentiment_counts,
    on=["day", "crypto"],
    how="left"
)

df_daily = df_daily.rename(columns={"day": "date"})

for col in ["positive", "negative", "neutral"]:
    if col not in df_daily.columns:
        df_daily[col] = 0

# MOVING AVERAGES
df_daily = df_daily.sort_values(["crypto", "date"])

df_daily["ma_7"] = (
    df_daily.groupby("crypto")["sentiment_mean"]
    .transform(lambda x: x.rolling(7, min_periods=1).mean())
)

df_daily["ma_30"] = (
    df_daily.groupby("crypto")["sentiment_mean"]
    .transform(lambda x: x.rolling(30, min_periods=1).mean())
)


df_final = df_daily.rename(columns={
    "positive": "positive_count",
    "negative": "negative_count",
    "neutral": "neutral_count"
})

df_final = df_final[
    [
        "date",
        "crypto",
        "sentiment_mean",
        "sentiment_std",
        "positive_count",
        "negative_count",
        "neutral_count",
        "ma_7",
        "ma_30"
    ]
]

df_final["date"] = df_final["date"].astype(str)

records = df_final.to_dict(orient="records")

# SAVE OUTPUT JSON
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

logging.info(f"Output JSON saved at: {OUTPUT_JSON}")
