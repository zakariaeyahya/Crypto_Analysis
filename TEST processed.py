# ==========================
# Imports
# ==========================
import pandas as pd
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import re
import os
from tqdm import tqdm
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Permet d'afficher la progression de apply
tqdm.pandas()

# ==========================
# Charger modèle spaCy
# ==========================
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# ==========================
# Stopwords crypto personnalisés
# ==========================
CRYPTO_STOPWORDS = {
    "crypto", "cryptocurrency", "bitcoin", "btc", "eth", "ethereum", "sol", "solana",
    "coin", "token", "blockchain", "altcoin", "hodl", "airdrop", "etf", "defi",
    "market", "price", "money", "buy", "sell", "trade", "trader", "investor",
    "bull", "bear", "ath", "dip", "pump", "dump", "liquidation",
    "source", "http", "https", "www", "com", "reddit", "twitter", "post", "comment",
    "say", "think", "people", "going", "really", "know", "see", "get", "make",
    "year", "day", "time"
}

# Fusion stopwords spaCy + crypto
all_stopwords = STOP_WORDS.union(CRYPTO_STOPWORDS)

# ==========================
# Fonction de prétraitement
# ==========================
def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    
    # Supprimer URLs, hashtags, mentions, ponctuation non lettres
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[@#]\w+', '', text)
    text = re.sub(r'[^a-zA-Z ]+', ' ', text)
    text = text.lower()
    
    doc = nlp(text)
    
    tokens = [
        token.lemma_.lower() for token in doc
        if token.lemma_.isalpha()
        and len(token.lemma_) > 2
        and token.lemma_.lower() not in all_stopwords
        and not token.is_stop
    ]
    
    return " ".join(tokens)

# ==========================
# Charger dataset
# ==========================
input_file = "C:\\Users\\DELL\\Downloads\\test_data.csv"  # <-- Chemin vers ton fichier test
df = pd.read_csv(input_file)

# ==========================
# Appliquer nettoyage avec tqdm
# ==========================
df["processed_text"] = df["text_content"].progress_apply(preprocess_text)

# ==========================
# Sauvegarde résultat
# ==========================
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

output_file = os.path.abspath(os.path.join(DATA_DIR, "processed_test_data.xlsx"))
df.to_excel(output_file, index=False)

logging.info("✅ Nettoyage COMPLET terminé !")
logging.info(f"✅ Nouveau fichier sauvegardé ici : {os.path.abspath(output_file)}")
