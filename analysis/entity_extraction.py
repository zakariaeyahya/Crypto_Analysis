import json
import pandas as pd
import re
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_PATH, "data")

ENTITIES_PATH = os.path.join(
    DATA_PATH, "bronze", "dictionnary", "entities.json"
)

CSV_PATH = os.path.join(
    DATA_PATH, "crypto_sent.csv"
)

OUTPUT_PATH = os.path.join(
    DATA_PATH, "silver", "enriched_data", "enriched_data.json"
)

logging.info("Starting tweet enrichment pipeline")


# LOAD REFERENCE FILES

try:
    with open(ENTITIES_PATH, "r", encoding="utf-8") as f:
        REF = json.load(f)
    logging.info("entities.json loaded successfully")
except Exception as e:
    logging.error("Failed to load entities.json", exc_info=True)
    raise e

CRYPTO_REF = REF["cryptos"]
EXCHANGE_REF = REF["exchanges"]
INFLUENCER_REF = REF["influencers"]
EVENT_REF = REF["events"]


try:
    df = pd.read_csv(CSV_PATH)
    logging.info("CSV file loaded successfully")
except Exception as e:
    logging.error("Failed to load crypto_senti_clean.csv", exc_info=True)
    raise e


def match_from_dict(text, ref_dict):
    """
    Generic matcher for cryptos, exchanges and influencers
    """
    text_lower = text.lower()
    found = []

    for name, aliases in ref_dict.items():
        for alias in aliases:
            if alias.lower() in text_lower:
                found.append(name)
                break

    return list(set(found))


def detect_events(text, events_ref):
    """
    Detect event types based on keyword matching
    """
    text_lower = text.lower()
    events = []

    for event_type, data in events_ref.items():
        for kw in data["keywords"]:
            if kw.replace("_", " ") in text_lower:
                events.append({"type": event_type})
                break

    return events


def detect_source(text):
    """
    Identify tweet source (original or retweet)
    """
    if isinstance(text, str) and text.startswith("RT @"):
        return "twitter_retweet"
    return "twitter"


output = []
total_rows = len(df)

logging.info(f"Processing {total_rows} tweets")

for index, row in df.iterrows():
    text = row["text"] if isinstance(row["text"], str) else ""

    cryptos = match_from_dict(text, CRYPTO_REF)
    influencers = match_from_dict(text, INFLUENCER_REF)
    exchanges = match_from_dict(text, EXCHANGE_REF)

    hashtags = re.findall(r"#\w+", text)
    mentions = re.findall(r"@\w+", text)

    record = {
        "id": str(row["id"]),
        "text": text,
        "date": pd.to_datetime(row["created_at"]).isoformat(),
        "source": detect_source(text),
        "crypto": cryptos,
        "sentiment": row["sentiment"],              
        "sentiment_score": float(row["score"]),
        "entities": list(set(cryptos + influencers + exchanges + hashtags + mentions)),
        "events": detect_events(text, EVENT_REF),
        "influencers": influencers
    }

    output.append(record)

    if index % 1000 == 0 and index > 0:
        logging.info(f"Processed {index}/{total_rows} tweets")



try:
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logging.info("JSON file successfully generated")
    logging.info(f"Output file: {OUTPUT_PATH}")

except Exception as e:
    logging.error("Failed to write output JSON file", exc_info=True)
    raise e
