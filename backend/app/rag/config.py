

import os
from pathlib import Path
from dotenv import load_dotenv

# =====================================================================
# CHARGER LES VARIABLES D'ENVIRONNEMENT
# =====================================================================
load_dotenv()

# =====================================================================
# CHEMINS
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# =====================================================================
# PINECONE
# =====================================================================
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "crypto-sentiment-rag")
PINECONE_CLOUD = "aws"
PINECONE_REGION = "us-east-1"

# =====================================================================
# EMBEDDING
# =====================================================================
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# =====================================================================
# LLM
# =====================================================================


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"


# =====================================================================
# RAG
# =====================================================================
RAG_TOP_K = 5
RAG_MIN_SCORE = 0.35  # Abaisse pour meilleur recall (Solana, requetes vagues)

# =====================================================================
# CHEMINS DES DONNÉES
# =====================================================================
DATA_PATHS = {
    "posts": DATA_DIR / "silver/enriched_data/crypto_sent_enriched_price.json",
    "timeseries": DATA_DIR / "gold/sentiment_timeseries.json",
    "correlation": DATA_DIR / "gold/sentiment_price_correlation.json",
    "lag": DATA_DIR / "gold/lag_analysis.json",
    "prices_btc": DATA_DIR / "bronze/BTC/historical_prices.csv",
    "prices_eth": DATA_DIR / "bronze/ETH/historical_prices.csv",
    "prices_sol": DATA_DIR / "bronze/SOL/historical_prices.csv",
}

# =====================================================================
# MAPPING CRYPTOS
# =====================================================================
CRYPTO_MAPPING = {
    "Bitcoin": "BTC",
    "Ethereum": "ETH",
    "Solana": "SOL",
}

# =====================================================================
# FAQ STATIQUES
# =====================================================================
FAQ_DATA = [
    {
        "question": "Comment fonctionne le score?",
        "answer": "Le score de sentiment mesure la tonalité des posts crypto entre -1 (négatif) et +1 (positif)."
    },
    {
        "question": "Qu'est-ce que Pearson?",
        "answer": "La corrélation de Pearson mesure la relation linéaire entre le sentiment et le prix."
    },
]