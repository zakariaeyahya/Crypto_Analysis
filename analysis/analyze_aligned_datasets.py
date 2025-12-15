"""
Script d'analyse des datasets alignés (ETH, BTC, Sentiment Crypto)
Utilise le logging au lieu de print pour une meilleure traçabilité
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime

# Configuration du logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Chemins des fichiers
DATA_DIR = Path(__file__).parent.parent / "data" / "silver" / "aligned_datasets"
ETH_FILE = DATA_DIR / "eth_prices_aligned.csv"
BTC_FILE = DATA_DIR / "btc_prices_aligned.csv"
SENTIMENT_FILE = DATA_DIR / "crypto_sent_aligned.csv"


def load_datasets():
    """Charge les trois datasets"""
    logger.info("=" * 60)
    logger.info("CHARGEMENT DES DATASETS")
    logger.info("=" * 60)
    
    try:
        eth_df = pd.read_csv(ETH_FILE)
        logger.info(f"✓ ETH chargé: {len(eth_df)} lignes depuis {ETH_FILE.name}")
    except Exception as e:
        logger.error(f"✗ Erreur chargement ETH: {e}")
        eth_df = None
    
    try:
        btc_df = pd.read_csv(BTC_FILE)
        logger.info(f"✓ BTC chargé: {len(btc_df)} lignes depuis {BTC_FILE.name}")
    except Exception as e:
        logger.error(f"✗ Erreur chargement BTC: {e}")
        btc_df = None
    
    try:
        sent_df = pd.read_csv(SENTIMENT_FILE)
        logger.info(f"✓ Sentiment chargé: {len(sent_df)} lignes depuis {SENTIMENT_FILE.name}")
    except Exception as e:
        logger.error(f"✗ Erreur chargement Sentiment: {e}")
        sent_df = None
    
    return eth_df, btc_df, sent_df


def analyze_price_dataset(df, crypto_name):
    """Analyse un dataset de prix (ETH ou BTC)"""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"ANALYSE DES PRIX {crypto_name}")
    logger.info("=" * 60)
    
    if df is None:
        logger.warning(f"Dataset {crypto_name} non disponible")
        return
    
    # Informations générales
    logger.info(f"Nombre de colonnes: {len(df.columns)}")
    logger.info(f"Colonnes: {list(df.columns)}")
    logger.info(f"Types de données:\n{df.dtypes.to_string()}")
    
    # Conversion de la date
    df['date'] = pd.to_datetime(df['date'])
    
    # Période couverte
    date_min = df['date'].min()
    date_max = df['date'].max()
    logger.info(f"Période: {date_min.strftime('%Y-%m-%d')} → {date_max.strftime('%Y-%m-%d')}")
    logger.info(f"Durée: {(date_max - date_min).days} jours")
    
    # Statistiques des prix
    logger.info("")
    logger.info(f"--- Statistiques Prix {crypto_name} ---")
    
    if 'price_open' in df.columns:
        logger.info(f"Prix Open  - Min: ${df['price_open'].min():.2f} | Max: ${df['price_open'].max():.2f} | Moyenne: ${df['price_open'].mean():.2f}")
    
    if 'price_close' in df.columns:
        logger.info(f"Prix Close - Min: ${df['price_close'].min():.2f} | Max: ${df['price_close'].max():.2f} | Moyenne: ${df['price_close'].mean():.2f}")
    
    if 'volume' in df.columns:
        logger.info(f"Volume     - Min: {df['volume'].min():,.0f} | Max: {df['volume'].max():,.0f} | Moyenne: {df['volume'].mean():,.0f}")
    
    # Variation des prix
    if 'price_close' in df.columns and 'price_open' in df.columns:
        df['daily_change'] = df['price_close'] - df['price_open']
        df['daily_change_pct'] = ((df['price_close'] - df['price_open']) / df['price_open']) * 100
        
        logger.info("")
        logger.info(f"--- Variations Journalières {crypto_name} ---")
        logger.info(f"Variation moyenne: {df['daily_change_pct'].mean():.2f}%")
        logger.info(f"Variation max positive: {df['daily_change_pct'].max():.2f}%")
        logger.info(f"Variation max négative: {df['daily_change_pct'].min():.2f}%")
        logger.info(f"Écart-type variation: {df['daily_change_pct'].std():.2f}%")
        
        # Jours positifs vs négatifs
        jours_positifs = (df['daily_change'] > 0).sum()
        jours_negatifs = (df['daily_change'] < 0).sum()
        jours_stables = (df['daily_change'] == 0).sum()
        logger.info(f"Jours positifs: {jours_positifs} ({jours_positifs/len(df)*100:.1f}%)")
        logger.info(f"Jours négatifs: {jours_negatifs} ({jours_negatifs/len(df)*100:.1f}%)")
        logger.info(f"Jours stables: {jours_stables}")
    
    # Valeurs manquantes
    missing = df.isnull().sum()
    if missing.sum() > 0:
        logger.warning(f"Valeurs manquantes détectées:\n{missing[missing > 0].to_string()}")
    else:
        logger.info("✓ Aucune valeur manquante")
    
    return df


def analyze_sentiment_dataset(df):
    """Analyse le dataset de sentiment"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("ANALYSE DU SENTIMENT CRYPTO")
    logger.info("=" * 60)
    
    if df is None:
        logger.warning("Dataset Sentiment non disponible")
        return
    
    # Informations générales
    logger.info(f"Nombre de colonnes: {len(df.columns)}")
    logger.info(f"Colonnes: {list(df.columns)}")
    logger.info(f"Types de données:\n{df.dtypes.to_string()}")
    
    # Conversion de la date
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])
        date_min = df['created_at'].min()
        date_max = df['created_at'].max()
        logger.info(f"Période: {date_min.strftime('%Y-%m-%d %H:%M')} → {date_max.strftime('%Y-%m-%d %H:%M')}")
        logger.info(f"Durée: {(date_max - date_min).days} jours")
    
    # Distribution des sentiments
    if 'sentiment' in df.columns:
        logger.info("")
        logger.info("--- Distribution des Sentiments ---")
        sentiment_counts = df['sentiment'].value_counts()
        total = len(df)
        for sentiment, count in sentiment_counts.items():
            logger.info(f"  {sentiment}: {count} ({count/total*100:.2f}%)")
    
    # Statistiques des scores
    if 'score' in df.columns:
        logger.info("")
        logger.info("--- Statistiques des Scores ---")
        logger.info(f"Score - Min: {df['score'].min():.4f} | Max: {df['score'].max():.4f}")
        logger.info(f"Score - Moyenne: {df['score'].mean():.4f} | Médiane: {df['score'].median():.4f}")
        logger.info(f"Score - Écart-type: {df['score'].std():.4f}")
        
        # Distribution par intervalles
        logger.info("")
        logger.info("--- Distribution des Scores par Intervalle ---")
        bins = [-1, -0.5, -0.1, 0.1, 0.5, 1]
        labels = ['Très négatif', 'Négatif', 'Neutre', 'Positif', 'Très positif']
        df['score_category'] = pd.cut(df['score'], bins=bins, labels=labels)
        score_dist = df['score_category'].value_counts()
        for cat in labels:
            count = score_dist.get(cat, 0)
            logger.info(f"  {cat}: {count} ({count/total*100:.2f}%)")
    
    # Analyse du texte
    if 'text' in df.columns:
        logger.info("")
        logger.info("--- Analyse des Textes ---")
        df['text_length'] = df['text'].astype(str).apply(len)
        logger.info(f"Longueur texte - Min: {df['text_length'].min()} | Max: {df['text_length'].max()}")
        logger.info(f"Longueur texte - Moyenne: {df['text_length'].mean():.1f}")
        
        # Textes vides
        empty_texts = df['text'].isna().sum() + (df['text'] == '').sum()
        logger.info(f"Textes vides/null: {empty_texts}")
    
    # Valeurs manquantes
    missing = df.isnull().sum()
    if missing.sum() > 0:
        logger.warning(f"Valeurs manquantes détectées:\n{missing[missing > 0].to_string()}")
    else:
        logger.info("✓ Aucune valeur manquante")
    
    return df


def analyze_temporal_alignment(eth_df, btc_df, sent_df):
    """Analyse l'alignement temporel entre les datasets"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("ANALYSE DE L'ALIGNEMENT TEMPOREL")
    logger.info("=" * 60)
    
    datasets = {}
    
    if eth_df is not None and 'date' in eth_df.columns:
        eth_df['date'] = pd.to_datetime(eth_df['date'])
        datasets['ETH'] = set(eth_df['date'].dt.date)
    
    if btc_df is not None and 'date' in btc_df.columns:
        btc_df['date'] = pd.to_datetime(btc_df['date'])
        datasets['BTC'] = set(btc_df['date'].dt.date)
    
    if sent_df is not None and 'created_at' in sent_df.columns:
        sent_df['created_at'] = pd.to_datetime(sent_df['created_at'])
        datasets['Sentiment'] = set(sent_df['created_at'].dt.date)
    
    if len(datasets) < 2:
        logger.warning("Pas assez de datasets pour analyser l'alignement")
        return
    
    # Période commune
    if len(datasets) == 3:
        common_dates = datasets['ETH'] & datasets['BTC'] & datasets['Sentiment']
        logger.info(f"Dates communes aux 3 datasets: {len(common_dates)} jours")
        
        if common_dates:
            min_common = min(common_dates)
            max_common = max(common_dates)
            logger.info(f"Période commune: {min_common} → {max_common}")
    
    # Comparaisons par paires
    for name1, dates1 in datasets.items():
        for name2, dates2 in datasets.items():
            if name1 < name2:
                common = dates1 & dates2
                only_in_1 = dates1 - dates2
                only_in_2 = dates2 - dates1
                logger.info(f"\n{name1} vs {name2}:")
                logger.info(f"  Dates communes: {len(common)}")
                logger.info(f"  Uniquement dans {name1}: {len(only_in_1)}")
                logger.info(f"  Uniquement dans {name2}: {len(only_in_2)}")


def generate_summary(eth_df, btc_df, sent_df):
    """Génère un résumé final de l'analyse"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("RÉSUMÉ DE L'ANALYSE")
    logger.info("=" * 60)
    
    summary = []
    
    if eth_df is not None:
        summary.append(f"ETH: {len(eth_df)} enregistrements de prix")
    if btc_df is not None:
        summary.append(f"BTC: {len(btc_df)} enregistrements de prix")
    if sent_df is not None:
        summary.append(f"Sentiment: {len(sent_df)} tweets/posts analysés")
    
    for item in summary:
        logger.info(f"• {item}")
    
    logger.info("")
    logger.info("Analyse terminée avec succès ✓")
    logger.info(f"Logs sauvegardés dans: {LOG_DIR}")


def main():
    """Fonction principale"""
    logger.info("=" * 60)
    logger.info("DÉMARRAGE DE L'ANALYSE DES DATASETS ALIGNÉS")
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Chargement
    eth_df, btc_df, sent_df = load_datasets()
    
    # Analyses individuelles
    eth_df = analyze_price_dataset(eth_df, "ETH")
    btc_df = analyze_price_dataset(btc_df, "BTC")
    sent_df = analyze_sentiment_dataset(sent_df)
    
    # Analyse de l'alignement
    analyze_temporal_alignment(eth_df, btc_df, sent_df)
    
    # Résumé
    generate_summary(eth_df, btc_df, sent_df)


if __name__ == "__main__":
    main()

