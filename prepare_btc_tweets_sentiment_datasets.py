"""
Script de préparation de datasets pour l'analyse corrélation sentiment Twitter / Prix Bitcoin.

Ce script crée deux datasets finaux :
1. Niveau tweet : btc_tweets_enriched_with_price.csv
2. Niveau jour : btc_tweets_with_market_daily.csv

Période : 2021-02-05 → 2021-08-21
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from datetime import datetime
import logging
from dateutil import parser
import re

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_tweets_file(file_path: str, chunk_size: int = 100000) -> pd.DataFrame:
    """
    Charge un fichier de tweets avec gestion d'encodage.
    Pour les gros fichiers, charge par chunks.
    
    Args:
        file_path: Chemin vers le fichier CSV
        chunk_size: Taille des chunks pour les gros fichiers
    
    Returns:
        DataFrame chargé
    """
    logger.info(f"Chargement du fichier de tweets: {file_path}")
    
    file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
    logger.info(f"  Taille du fichier: {file_size_mb:.2f} MB")
    
    # Pour les gros fichiers (>100MB), charger par chunks
    if file_size_mb > 100:
        logger.info(f"  Fichier volumineux détecté, chargement par chunks de {chunk_size} lignes...")
        chunks = []
        
        try:
            for chunk in pd.read_csv(file_path, encoding='utf-8', low_memory=False, chunksize=chunk_size):
                chunks.append(chunk)
                if len(chunks) % 10 == 0:
                    logger.info(f"    Chunks chargés: {len(chunks)} ({len(chunks) * chunk_size} lignes estimées)")
        except UnicodeDecodeError:
            logger.warning(f"  Encodage UTF-8 échoué, tentative avec latin-1...")
            chunks = []
            for chunk in pd.read_csv(file_path, encoding='latin-1', low_memory=False, chunksize=chunk_size):
                chunks.append(chunk)
                if len(chunks) % 10 == 0:
                    logger.info(f"    Chunks chargés: {len(chunks)} ({len(chunks) * chunk_size} lignes estimées)")
        
        df = pd.concat(chunks, ignore_index=True)
    else:
        # Essayer UTF-8 d'abord, puis latin-1 en fallback
        try:
            df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
        except UnicodeDecodeError:
            logger.warning(f"  Encodage UTF-8 échoué, tentative avec latin-1...")
            df = pd.read_csv(file_path, encoding='latin-1', low_memory=False)
    
    logger.info(f"  Fichier chargé: {len(df)} lignes, {len(df.columns)} colonnes")
    logger.info(f"  Colonnes: {list(df.columns)}")
    
    return df


def normalize_tweet_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise et renomme les colonnes du dataset de tweets.
    
    Args:
        df: DataFrame brut des tweets
    
    Returns:
        DataFrame avec colonnes normalisées
    """
    logger.info("Normalisation des colonnes...")
    
    result_df = df.copy()
    
    # Mapping des colonnes possibles vers les noms standardisés
    column_mapping = {}
    
    # Identifiant du tweet
    if 'id' in result_df.columns:
        column_mapping['id'] = 'tweet_id'
    elif 'tweet_id' not in result_df.columns:
        result_df['tweet_id'] = result_df.index
    
    # Date/heure
    date_cols = ['date', 'Date', 'timestamp', 'created_at', 'datetime']
    for col in date_cols:
        if col in result_df.columns:
            column_mapping[col] = 'date_time'
            break
    
    # Texte du tweet
    text_cols = ['Tweet', 'text', 'tweet', 'tweet_text', 'content']
    for col in text_cols:
        if col in result_df.columns:
            column_mapping[col] = 'tweet_text'
            break
    
    # Informations utilisateur
    user_mappings = {
        'Screen_name': 'user_name',
        'user_name': 'user_name',
        'username': 'user_name',
        'user_location': 'user_location',
        'user_description': 'user_description',
        'user_created': 'user_created',
        'user_followers': 'user_followers',
        'followers_count': 'user_followers',
        'user_friends': 'user_friends',
        'friends_count': 'user_friends',
        'user_favourites': 'user_favourites',
        'favourites_count': 'user_favourites',
        'user_verified': 'user_verified',
        'verified': 'user_verified'
    }
    
    for old_col, new_col in user_mappings.items():
        if old_col in result_df.columns:
            column_mapping[old_col] = new_col
    
    # Sentiment - chercher la colonne finale de classe
    sentiment_label_cols = ['New_Sentiment_State', 'Sentiment', 'sentiment', 'sentiment_label', 'label']
    for col in sentiment_label_cols:
        if col in result_df.columns:
            column_mapping[col] = 'sentiment_label'
            break
    
    # Score de sentiment (optionnel)
    sentiment_score_cols = ['New_Sentiment_Score', 'sent_score', 'polarity_score', 'sentiment_score']
    for col in sentiment_score_cols:
        if col in result_df.columns:
            column_mapping[col] = 'sentiment_score'
            break
    
    # Appliquer le mapping
    result_df = result_df.rename(columns=column_mapping)
    
    logger.info(f"  Colonnes normalisées: {list(result_df.columns)}")
    
    return result_df


def parse_twitter_date(date_str):
    """
    Parse une date Twitter en format datetime UTC.
    
    Args:
        date_str: String de date (format Twitter ou ISO)
    
    Returns:
        datetime ou NaT si invalide
    """
    if pd.isna(date_str):
        return pd.NaT
    
    try:
        # Essayer de parser avec dateutil (gère plusieurs formats)
        return parser.parse(str(date_str), default=datetime(2021, 1, 1))
    except:
        return pd.NaT


def clean_and_normalize_tweets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et normalise les données de tweets.
    
    Args:
        df: DataFrame avec colonnes normalisées
    
    Returns:
        DataFrame nettoyé
    """
    logger.info("Nettoyage des tweets...")
    
    initial_count = len(df)
    
    # 1. Supprimer les lignes avec tweet_text vide ou null
    df = df[df['tweet_text'].notna() & (df['tweet_text'].astype(str).str.strip() != '')].copy()
    logger.info(f"  Après suppression tweets vides: {len(df)} lignes ({initial_count - len(df)} supprimées)")
    
    # 2. Parser et nettoyer les dates
    if 'date_time' in df.columns:
        df['date_time'] = df['date_time'].apply(parse_twitter_date)
        df = df[df['date_time'].notna()].copy()
        logger.info(f"  Après nettoyage dates: {len(df)} lignes")
        
        # Créer colonne date journalière
        df['date'] = df['date_time'].dt.date.astype(str)
    else:
        logger.error("Colonne date_time manquante après normalisation!")
        return pd.DataFrame()
    
    # 3. Filtrer sur la période 2021-02-05 → 2021-08-21
    start_date = pd.to_datetime("2021-02-05")
    end_date = pd.to_datetime("2021-08-21")
    df = df[(df['date_time'] >= start_date) & (df['date_time'] <= end_date)].copy()
    logger.info(f"  Après filtrage période 2021: {len(df)} lignes")
    
    # 4. Optionnel : supprimer les retweets (commencent par "RT @")
    df['is_retweet'] = df['tweet_text'].astype(str).str.startswith('RT @')
    retweet_count = df['is_retweet'].sum()
    logger.info(f"  Retweets détectés: {retweet_count} ({retweet_count/len(df)*100:.1f}%)")
    # On garde les retweets pour l'instant, mais on peut les filtrer plus tard si besoin
    
    # 5. Normaliser le sentiment
    if 'sentiment_label' in df.columns:
        # Nettoyer les labels (enlever crochets, guillemets, etc.)
        df['sentiment_label'] = df['sentiment_label'].astype(str).str.replace(r"['\[\]]", '', regex=True).str.strip().str.lower()
        
        # Standardiser en 3 classes
        sentiment_mapping = {
            'positive': 'positive',
            'pos': 'positive',
            '1': 'positive',
            '1.0': 'positive',
            'negative': 'negative',
            'neg': 'negative',
            '-1': 'negative',
            '-1.0': 'negative',
            'neutral': 'neutral',
            'neu': 'neutral',
            '0': 'neutral',
            '0.0': 'neutral'
        }
        
        df['sentiment_label'] = df['sentiment_label'].map(sentiment_mapping).fillna('neutral')
        
        # Créer variable numérique
        sentiment_numeric_map = {'negative': -1, 'neutral': 0, 'positive': 1}
        df['sentiment_numeric'] = df['sentiment_label'].map(sentiment_numeric_map)
        
        logger.info(f"  Distribution sentiment: {df['sentiment_label'].value_counts().to_dict()}")
    else:
        logger.warning("Colonne sentiment_label manquante!")
        df['sentiment_label'] = 'neutral'
        df['sentiment_numeric'] = 0
    
    # 6. Normaliser sentiment_score si présent
    if 'sentiment_score' in df.columns:
        # S'assurer que c'est numérique et dans [-1, 1]
        df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce')
        # Normaliser si nécessaire (si > 1 ou < -1)
        if df['sentiment_score'].notna().any():
            max_score = df['sentiment_score'].abs().max()
            if max_score > 1:
                df['sentiment_score'] = df['sentiment_score'] / max_score
    else:
        # Utiliser sentiment_numeric comme score
        df['sentiment_score'] = df['sentiment_numeric']
    
    # 7. Nettoyer les colonnes utilisateur (convertir en numérique si possible)
    user_numeric_cols = ['user_followers', 'user_friends', 'user_favourites']
    for col in user_numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    if 'user_verified' in df.columns:
        # Convertir en booléen
        df['user_verified'] = df['user_verified'].astype(str).str.lower().isin(['true', '1', 'yes', 'verified'])
    
    logger.info(f"  Dataset nettoyé final: {len(df)} lignes")
    
    return df


def load_btc_prices(file_path: str = "data/bronze/BTC/historical_prices.csv") -> pd.DataFrame:
    """
    Charge et prépare les prix BTC.
    
    Args:
        file_path: Chemin vers le fichier de prix
    
    Returns:
        DataFrame avec prix BTC préparés
    """
    logger.info(f"Chargement des prix BTC: {file_path}")
    
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date']).dt.date.astype(str)
    
    # Renommer les colonnes
    df = df.rename(columns={
        'price_open': 'btc_open',
        'price_close': 'btc_close',
        'volume': 'btc_volume'
    })
    
    # Créer High et Low si absents (utiliser Close comme approximation)
    if 'High' not in df.columns and 'high' not in df.columns:
        df['btc_high'] = df['btc_close']
    else:
        high_col = 'High' if 'High' in df.columns else 'high'
        df['btc_high'] = df[high_col]
    
    if 'Low' not in df.columns and 'low' not in df.columns:
        df['btc_low'] = df['btc_close']
    else:
        low_col = 'Low' if 'Low' in df.columns else 'low'
        df['btc_low'] = df[low_col]
    
    # Calculer le retour journalier
    df = df.sort_values('date')
    df['btc_return'] = df['btc_close'].pct_change()
    
    # Filtrer sur la période 2021-02-05 → 2021-08-21
    start_date = "2021-02-05"
    end_date = "2021-08-21"
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()
    
    logger.info(f"  Prix BTC chargés: {len(df)} jours")
    logger.info(f"  Période: {df['date'].min()} → {df['date'].max()}")
    
    return df


def create_tweet_level_dataset(tweets_df: pd.DataFrame, prices_df: pd.DataFrame, output_path: str):
    """
    Crée le dataset niveau tweet enrichi avec les prix BTC.
    
    Args:
        tweets_df: DataFrame des tweets nettoyés
        prices_df: DataFrame des prix BTC
        output_path: Chemin de sortie
    """
    logger.info("Création du dataset niveau tweet...")
    
    # Jointure left join sur date
    result_df = tweets_df.merge(
        prices_df[['date', 'btc_open', 'btc_high', 'btc_low', 'btc_close', 'btc_volume', 'btc_return']],
        on='date',
        how='left'
    )
    
    # Sélectionner et ordonner les colonnes
    columns_order = [
        'tweet_id',
        'date_time',
        'date',
        'tweet_text',
        'sentiment_label',
        'sentiment_numeric',
        'sentiment_score',
        'user_name',
        'user_location',
        'user_description',
        'user_created',
        'user_followers',
        'user_friends',
        'user_favourites',
        'user_verified',
        'btc_open',
        'btc_high',
        'btc_low',
        'btc_close',
        'btc_volume',
        'btc_return',
        'is_retweet'
    ]
    
    # Garder seulement les colonnes présentes
    available_cols = [col for col in columns_order if col in result_df.columns]
    result_df = result_df[available_cols]
    
    # Supprimer les lignes sans prix BTC (dates sans données de marché)
    before_count = len(result_df)
    result_df = result_df[result_df['btc_close'].notna()].copy()
    after_count = len(result_df)
    logger.info(f"  Lignes avec prix BTC: {after_count} ({before_count - after_count} supprimées)")
    
    # Trier par date
    result_df = result_df.sort_values(['date', 'date_time']).reset_index(drop=True)
    
    # Sauvegarder
    result_df.to_csv(output_path, index=False)
    logger.info(f"  Dataset sauvegardé: {output_path}")
    logger.info(f"  Nombre de tweets: {len(result_df)}")
    logger.info(f"  Période: {result_df['date'].min()} → {result_df['date'].max()}")
    
    return result_df


def create_daily_aggregated_dataset(tweets_df: pd.DataFrame, prices_df: pd.DataFrame, output_path: str):
    """
    Crée le dataset niveau jour avec sentiment agrégé et prix BTC.
    
    Args:
        tweets_df: DataFrame des tweets nettoyés
        prices_df: DataFrame des prix BTC
        output_path: Chemin de sortie
    """
    logger.info("Création du dataset niveau jour (agrégé)...")
    
    # Agrégation par date
    agg_dict = {
        'tweet_id': 'count',  # Nombre de tweets
        'sentiment_numeric': 'mean'  # Moyenne du sentiment numérique
    }
    
    # Ajouter les colonnes optionnelles si présentes
    if 'user_verified' in tweets_df.columns:
        agg_dict['user_verified'] = 'sum'
    if 'sentiment_score' in tweets_df.columns:
        agg_dict['sentiment_score'] = 'mean'
    
    daily_agg = tweets_df.groupby('date').agg(agg_dict).reset_index()
    
    # Renommer les colonnes
    rename_map = {
        'tweet_id': 'n_tweets',
        'sentiment_numeric': 'sentiment_mean'
    }
    if 'user_verified' in daily_agg.columns:
        rename_map['user_verified'] = 'n_verified'
    if 'sentiment_score' in daily_agg.columns:
        rename_map['sentiment_score'] = 'sentiment_score_mean'
    
    daily_agg = daily_agg.rename(columns=rename_map)
    
    # Ajouter les colonnes manquantes avec valeurs par défaut
    if 'n_verified' not in daily_agg.columns:
        daily_agg['n_verified'] = 0
    if 'sentiment_score_mean' not in daily_agg.columns:
        daily_agg['sentiment_score_mean'] = daily_agg['sentiment_mean']
    
    # Calculer les comptes de sentiment par jour
    sentiment_counts = tweets_df.groupby(['date', 'sentiment_label']).size().unstack(fill_value=0)
    daily_agg = daily_agg.merge(sentiment_counts, left_on='date', right_index=True, how='left')
    
    # Renommer les colonnes de sentiment
    if 'positive' in daily_agg.columns:
        daily_agg = daily_agg.rename(columns={'positive': 'n_positive'})
    else:
        daily_agg['n_positive'] = 0
    
    if 'negative' in daily_agg.columns:
        daily_agg = daily_agg.rename(columns={'negative': 'n_negative'})
    else:
        daily_agg['n_negative'] = 0
    
    if 'neutral' in daily_agg.columns:
        daily_agg = daily_agg.rename(columns={'neutral': 'n_neutral'})
    else:
        daily_agg['n_neutral'] = 0
    
    # Calculer les ratios
    daily_agg['ratio_positive'] = daily_agg['n_positive'] / daily_agg['n_tweets']
    daily_agg['ratio_negative'] = daily_agg['n_negative'] / daily_agg['n_tweets']
    daily_agg['ratio_neutral'] = daily_agg['n_neutral'] / daily_agg['n_tweets']
    daily_agg['ratio_verified'] = daily_agg['n_verified'] / daily_agg['n_tweets']
    
    # Calculer les statistiques de followers si disponible
    if 'user_followers' in tweets_df.columns and tweets_df['user_followers'].notna().any():
        followers_stats = tweets_df.groupby('date')['user_followers'].agg(['mean', 'median']).reset_index()
        followers_stats.columns = ['date', 'followers_mean', 'followers_median']
        daily_agg = daily_agg.merge(followers_stats, on='date', how='left')
        daily_agg['followers_mean'] = daily_agg['followers_mean'].fillna(0)
        daily_agg['followers_median'] = daily_agg['followers_median'].fillna(0)
    else:
        daily_agg['followers_mean'] = 0
        daily_agg['followers_median'] = 0
    
    # Renommer pour clarté
    daily_agg = daily_agg.rename(columns={
        'sentiment_mean': 'sentiment_mean',
        'sentiment_score_mean': 'sentiment_score_mean'
    })
    
    # Joindre avec les prix BTC
    result_df = daily_agg.merge(
        prices_df[['date', 'btc_open', 'btc_high', 'btc_low', 'btc_close', 'btc_volume', 'btc_return']],
        on='date',
        how='inner'  # Inner join : garder seulement les jours avec tweets ET prix
    )
    
    # Ordre des colonnes
    columns_order = [
        'date',
        'n_tweets',
        'n_positive',
        'n_negative',
        'n_neutral',
        'ratio_positive',
        'ratio_negative',
        'ratio_neutral',
        'sentiment_mean',
        'sentiment_score_mean',
        'n_verified',
        'ratio_verified',
        'followers_mean',
        'followers_median',
        'btc_open',
        'btc_high',
        'btc_low',
        'btc_close',
        'btc_volume',
        'btc_return'
    ]
    
    result_df = result_df[columns_order]
    result_df = result_df.sort_values('date').reset_index(drop=True)
    
    # Sauvegarder
    result_df.to_csv(output_path, index=False)
    logger.info(f"  Dataset sauvegardé: {output_path}")
    logger.info(f"  Nombre de jours: {len(result_df)}")
    logger.info(f"  Période: {result_df['date'].min()} → {result_df['date'].max()}")
    
    return result_df


def main():
    """
    Fonction principale de préparation des datasets.
    """
    logger.info("="*60)
    logger.info("PRÉPARATION DES DATASETS BITCOIN TWEETS + SENTIMENT")
    logger.info("="*60)
    
    # Configuration
    OUTPUT_DIR = "data/analysis_2021"
    
    # Chemins des fichiers d'entrée (à adapter selon vos fichiers)
    TWEETS_FILES = [
        "data/bronze/kaggle/gautamchettiar_bitcoin-sentiment-analysis-twitter-data/bitcoin_tweets1000000.csv",
        "data/bronze/kaggle/aisolutions353_btc-tweets-sentiment/BTC_Tweets_Updated.csv"
    ]
    
    BTC_PRICES_FILE = "data/bronze/BTC/historical_prices.csv"
    
    # Créer le répertoire de sortie
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Charger les tweets (essayer plusieurs fichiers)
    all_tweets = []
    for tweets_file in TWEETS_FILES:
        if Path(tweets_file).exists():
            try:
                df = load_tweets_file(tweets_file)
                df = normalize_tweet_columns(df)
                
                # Vérifier rapidement la période couverte (avant nettoyage complet)
                if 'date_time' in df.columns:
                    df_temp = df.copy()
                    df_temp['date_time'] = df_temp['date_time'].apply(parse_twitter_date)
                    df_temp = df_temp[df_temp['date_time'].notna()]
                    if len(df_temp) > 0:
                        date_range = f"{df_temp['date_time'].min()} → {df_temp['date_time'].max()}"
                        logger.info(f"  Période couverte: {date_range}")
                
                all_tweets.append(df)
                logger.info(f"  Fichier chargé avec succès: {tweets_file}")
            except Exception as e:
                logger.warning(f"  Erreur lors du chargement de {tweets_file}: {e}")
                import traceback
                logger.debug(traceback.format_exc())
        else:
            logger.warning(f"  Fichier non trouvé: {tweets_file}")
    
    if not all_tweets:
        logger.error("Aucun fichier de tweets chargé! Vérifiez les chemins.")
        return
    
    # Concaténer tous les datasets de tweets
    tweets_df = pd.concat(all_tweets, ignore_index=True)
    logger.info(f"Total tweets chargés: {len(tweets_df)}")
    
    # Supprimer les doublons basés sur tweet_id si disponible
    if 'tweet_id' in tweets_df.columns:
        before_dedup = len(tweets_df)
        tweets_df = tweets_df.drop_duplicates(subset=['tweet_id'], keep='first')
        logger.info(f"  Après déduplication: {len(tweets_df)} tweets ({before_dedup - len(tweets_df)} doublons supprimés)")
    
    # 2. Nettoyer et normaliser les tweets
    tweets_df = clean_and_normalize_tweets(tweets_df)
    
    if len(tweets_df) == 0:
        logger.error("Aucun tweet valide après nettoyage!")
        return
    
    # 3. Charger les prix BTC
    prices_df = load_btc_prices(BTC_PRICES_FILE)
    
    if len(prices_df) == 0:
        logger.error("Aucun prix BTC chargé!")
        return
    
    # 4. Créer le dataset niveau tweet
    tweet_output = output_path / "btc_tweets_enriched_with_price.csv"
    create_tweet_level_dataset(tweets_df, prices_df, str(tweet_output))
    
    # 5. Créer le dataset niveau jour
    daily_output = output_path / "btc_tweets_with_market_daily.csv"
    create_daily_aggregated_dataset(tweets_df, prices_df, str(daily_output))
    
    # 6. Résumé final
    logger.info("\n" + "="*60)
    logger.info("RÉSUMÉ FINAL")
    logger.info("="*60)
    logger.info(f"\nFichiers créés:")
    logger.info(f"  1. {tweet_output}")
    logger.info(f"  2. {daily_output}")
    logger.info(f"\nPériode d'analyse: 2021-02-05 → 2021-08-21")
    logger.info("\nPréparation terminée avec succès!")


if __name__ == "__main__":
    main()

