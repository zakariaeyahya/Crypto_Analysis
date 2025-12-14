# =========================
# IMPORTS
# =========================
import json
import re
import spacy
import pandas as pd
import logging

# =========================
# LOGGING
# =========================
logging.basicConfig(
    filename=r"C:\Users\hp\Crypto_Analysis\data_enri\ner_pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("NER Pipeline initialized.")

# =========================
# 1. LOAD ENTITIES.JSON
# =========================
ENTITIES_FILE = r"C:\Users\hp\Crypto_Analysis\data\bronze\dictionnary\entities.json"
with open(ENTITIES_FILE, "r", encoding="utf-8") as f:
    entities = json.load(f)

logging.info(f"Entities loaded: {list(entities.keys())}")

# =========================
# 2. BUILD REGEX PATTERNS
# =========================
def generate_regex(entity_dict):
    patterns = {}
    for key, variants in entity_dict.items():
        escaped = [re.escape(v) for v in variants]
        pattern = r"\b(" + "|".join(escaped) + r")\b"
        patterns[key] = pattern
    return patterns

crypto_patterns = generate_regex(entities["cryptos"])
exchange_patterns = generate_regex(entities["exchanges"])
influencer_patterns = generate_regex(entities["influencers"])

all_patterns = {
    "cryptos": crypto_patterns,
    "exchanges": exchange_patterns,
    "influencers": influencer_patterns
}

logging.info("Regex patterns generated successfully.")

# =========================
# 3. REGEX ENTITY DETECTION
# =========================
def detect_entities(text, patterns_dict):
    found = {"cryptos": [], "exchanges": [], "influencers": []}

    for entity_type in patterns_dict:
        for name, pattern in patterns_dict[entity_type].items():
            if re.search(pattern, text, flags=re.IGNORECASE):
                found[entity_type].append(name)

    return found

# =========================
# 4. SPACY NER
# =========================
logging.info("Loading spaCy model.")
nlp = spacy.load("en_core_web_sm")

def apply_spacy_ner(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

# =========================
# 5. CSV ENRICHMENT PIPELINE
# =========================
def enrich_dataset_csv(input_csv_path, output_csv_path):
    logging.info(f"Processing dataset: {input_csv_path}")

    df = pd.read_csv(input_csv_path, encoding="utf-8")
    logging.info(f"Dataset loaded with {len(df)} rows.")

    # sécurité texte manquant
    df["text"] = df["text"].fillna("")

    df["spacy_entities"] = df["text"].apply(apply_spacy_ner)
    df["cryptos"] = df["text"].apply(lambda t: detect_entities(t, all_patterns)["cryptos"])
    df["exchanges"] = df["text"].apply(lambda t: detect_entities(t, all_patterns)["exchanges"])
    df["influencers"] = df["text"].apply(lambda t: detect_entities(t, all_patterns)["influencers"])

    df.to_csv(output_csv_path, index=False, encoding="utf-8")
    logging.info(f"Saved enriched dataset: {output_csv_path}")

    return df

# =========================
# 6. RUN
# =========================
# =========================
# 6. RUN
# =========================
if __name__ == "__main__":

    INPUT_CSV = r"data\crypto_sent.csv"
    OUTPUT_CSV = r"data\silver\enriched_data\enriched_data.csv"

    logging.info("Starting NER enrichment for CSV dataset.")
    enrich_dataset_csv(INPUT_CSV, OUTPUT_CSV)
    logging.info("NER enrichment completed.")

