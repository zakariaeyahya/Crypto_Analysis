# ==========================
# Imports
# ==========================
import pandas as pd
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import re
import os
from tqdm import tqdm
import json
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
def load_stopwords_from_json(file_path):
    """Charge les stopwords depuis un fichier JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            stopwords_list = json.load(f)
        return set(stopwords_list)
    except FileNotFoundError:
        logging.error(f"Le fichier de stopwords '{file_path}' n'a pas été trouvé. Utilisation d'une liste vide.")
        return set()
    except json.JSONDecodeError:
        logging.error(f"Erreur de décodage JSON dans le fichier '{file_path}'. Utilisation d'une liste vide.")
        return set()

# Charger les stopwords depuis le fichier externe
CRYPTO_STOPWORDS = load_stopwords_from_json("C:\\Users\\Hiba\\Desktop\\S9\\crypto\\crypto_stopwords.json")
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
input_file = "C:\\Users\\DELL\\Downloads\\test_data.xlsx"  # <-- Chemin vers ton fichier test
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
logging.info(f"Data directory created at: {os.path.abspath(DATA_DIR)}")
logging.info(f"DATA_DIR value: {DATA_DIR}")

# Supprimer l'ancien fichier .xlsx s'il existe
old_output_file = os.path.abspath("processed_test_data.xlsx")
if os.path.exists(old_output_file):
    os.remove(old_output_file)

output_file = os.path.abspath(os.path.join(DATA_DIR, "processed_test_data.xlsx"))
df.to_csv(output_file, index=False)

logging.info(" Cleaning COMPLETELY finished!")
logging.info(f" New file saved here: {os.path.abspath(output_file)}")
