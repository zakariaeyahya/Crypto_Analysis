# ==========================
# Imports
# ==========================
import pandas as pd
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import re
import os
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
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
input_file = "C:\\Users\\DELL\\Downloads\\train_data.csv"
df = pd.read_csv(input_file)

# ==========================
# Appliquer nettoyage avec tqdm
# ==========================
df["processed_text"] = df["text_content"].progress_apply(preprocess_text)

# ==========================
# Analyse de sentiment VADER
# ==========================
analyzer = SentimentIntensityAnalyzer()

# Appliquer VADER sur le texte traité
df['vader_scores'] = df['processed_text'].progress_apply(lambda text: analyzer.polarity_scores(text))

# Extraire les scores dans des colonnes séparées
df['vader_compound'] = df['vader_scores'].apply(lambda score_dict: score_dict['compound'])
df['vader_pos'] = df['vader_scores'].apply(lambda score_dict: score_dict['pos'])
df['vader_neg'] = df['vader_scores'].apply(lambda score_dict: score_dict['neg'])
df['vader_neu'] = df['vader_scores'].apply(lambda score_dict: score_dict['neu'])

# Convertir le score compound en sentiment
def vader_to_sentiment(compound):
    if compound >= 0.05:
        return 'positive'
    elif compound <= -0.05:
        return 'negative'
    else:
        return 'neutral'

df['vader_sentiment'] = df['vader_compound'].apply(vader_to_sentiment)

# ==========================
# Évaluation du modèle VADER
# ==========================
# Assurez-vous que votre CSV a une colonne 'sentiment' avec les vraies étiquettes
if 'sentiment' in df.columns:
    y_true = df['sentiment']
    y_pred = df['vader_sentiment']

    logging.info("\n📊 Évaluation de VADER :")
    logging.info("="*25)
    logging.info(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
    logging.info("\nClassification Report:")
    logging.info(classification_report(y_true, y_pred, digits=4))
    logging.info("\nConfusion Matrix:")
    logging.info(confusion_matrix(y_true, y_pred, labels=['positive', 'neutral', 'negative']))
else:
    logging.info("\n⚠️  Colonne 'sentiment' non trouvée. L'évaluation des performances est ignorée.")

# ==========================
# Sauvegarde résultat
# ==========================
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

output_file = os.path.abspath(os.path.join(DATA_DIR, "processed_train_data.xlsx"))
df.to_excel(output_file, index=False)

logging.info("\n✅ Analyse VADER et nettoyage terminés !")
logging.info(f"✅ Nouveau fichier sauvegardé ici : {os.path.abspath(output_file)}")
