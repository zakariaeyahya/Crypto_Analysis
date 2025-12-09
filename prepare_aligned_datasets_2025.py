"""
Script de préparation de datasets alignés pour l'analyse Bitcoin/Sentiment 2025.

Ce script crée des datasets alignés sur la période 2025-02-05 → 2025-08-21
où des tweets avec sentiment sont disponibles.

Objectif : préparer les données, pas d'analyse statistique.
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_output_directory(output_dir: str = "data/analysis_2025"):
    """
    Crée le répertoire de sortie si nécessaire.
    
    Args:
        output_dir: Chemin du répertoire de sortie
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Répertoire de sortie créé/vérifié: {output_path}")
    return output_path


def load_and_filter_sentiment_data(
    sentiment_file: str = "data/gold/bitcoin_sentiment/btc_sentiment_daily.csv",
    start_date: str = "2025-02-05",
    end_date: str = "2025-08-21"
) -> pd.DataFrame:
    """
    Charge et filtre les données de sentiment Bitcoin sur la période 2025.
    
    Args:
        sentiment_file: Chemin vers le fichier de sentiment
        start_date: Date de début (YYYY-MM-DD)
        end_date: Date de fin (YYYY-MM-DD)
    
    Returns:
        DataFrame filtré sur la période 2025
    """
    logger.info(f"Chargement du fichier de sentiment: {sentiment_file}")
    
    sentiment_path = Path(sentiment_file)
    if not sentiment_path.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {sentiment_file}")
    
    df = pd.read_csv(sentiment_path)
    df['date'] = pd.to_datetime(df['date'])
    
    logger.info(f"Données chargées: {len(df)} lignes")
    logger.info(f"Plage de dates originale: {df['date'].min().date()} → {df['date'].max().date()}")
    
    # Filtrer sur la période 2025 (exclure 2018-03-23)
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    df_filtered = df[(df['date'] >= start) & (df['date'] <= end)].copy()
    df_filtered = df_filtered.sort_values('date').reset_index(drop=True)
    
    logger.info(f"Données filtrées sur {start_date} → {end_date}: {len(df_filtered)} jours")
    logger.info(f"Plage de dates filtrée: {df_filtered['date'].min().date()} → {df_filtered['date'].max().date()}")
    
    return df_filtered


def load_and_filter_crypto_prices(
    crypto_file: str,
    symbol: str,
    start_date: str = "2025-02-05",
    end_date: str = "2025-08-21"
) -> pd.DataFrame:
    """
    Charge et filtre les prix d'une cryptomonnaie sur la période 2025.
    
    Args:
        crypto_file: Chemin vers le fichier de prix
        symbol: Symbole de la cryptomonnaie (BTC, ETH, SOL)
        start_date: Date de début (YYYY-MM-DD)
        end_date: Date de fin (YYYY-MM-DD)
    
    Returns:
        DataFrame filtré avec colonnes renommées
    """
    logger.info(f"Chargement des prix {symbol}: {crypto_file}")
    
    crypto_path = Path(crypto_file)
    if not crypto_path.exists():
        logger.warning(f"Fichier non trouvé: {crypto_file}")
        return pd.DataFrame()
    
    df = pd.read_csv(crypto_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Filtrer sur la période 2025
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    df_filtered = df[(df['date'] >= start) & (df['date'] <= end)].copy()
    df_filtered = df_filtered.sort_values('date').reset_index(drop=True)
    
    # Renommer les colonnes pour distinguer les cryptos
    df_filtered = df_filtered.rename(columns={
        'price_open': f'Open_{symbol}',
        'price_close': f'Close_{symbol}',
        'volume': f'Volume_{symbol}'
    })
    
    # Ajouter High et Low si disponibles (sinon utiliser Close pour High et Low)
    if 'High' not in df_filtered.columns and 'Low' not in df_filtered.columns:
        df_filtered[f'High_{symbol}'] = df_filtered[f'Close_{symbol}']
        df_filtered[f'Low_{symbol}'] = df_filtered[f'Close_{symbol}']
    else:
        if 'High' in df_filtered.columns:
            df_filtered = df_filtered.rename(columns={'High': f'High_{symbol}'})
        if 'Low' in df_filtered.columns:
            df_filtered = df_filtered.rename(columns={'Low': f'Low_{symbol}'})
    
    # Calculer le rendement de clôture
    df_filtered[f'return_close_{symbol}'] = df_filtered[f'Close_{symbol}'].pct_change()
    
    # Garder seulement les colonnes nécessaires
    cols_to_keep = ['date', f'Open_{symbol}', f'High_{symbol}', f'Low_{symbol}', 
                     f'Close_{symbol}', f'Volume_{symbol}', f'return_close_{symbol}']
    df_filtered = df_filtered[cols_to_keep]
    
    logger.info(f"Prix {symbol} filtrés: {len(df_filtered)} jours")
    
    return df_filtered


def create_btc_sentiment_dataset(
    sentiment_df: pd.DataFrame,
    output_dir: Path,
    filename: str = "btc_prices_sentiment_2025.csv"
) -> str:
    """
    Crée le dataset BTC + Sentiment pour 2025.
    
    Args:
        sentiment_df: DataFrame de sentiment filtré
        output_dir: Répertoire de sortie
        filename: Nom du fichier de sortie
    
    Returns:
        Chemin du fichier créé
    """
    logger.info("Création du dataset BTC + Sentiment 2025...")
    
    # Le DataFrame sentiment_df contient déjà les prix BTC (Open, High, Low, Close, Volume)
    # et tous les indicateurs de sentiment
    
    output_path = output_dir / filename
    sentiment_df.to_csv(output_path, index=False)
    
    logger.info(f"Dataset sauvegardé: {output_path}")
    logger.info(f"  Nombre de jours: {len(sentiment_df)}")
    logger.info(f"  Période: {sentiment_df['date'].min().date()} → {sentiment_df['date'].max().date()}")
    logger.info(f"  Colonnes: {len(sentiment_df.columns)}")
    
    return str(output_path)


def create_multi_crypto_dataset(
    sentiment_df: pd.DataFrame,
    btc_prices_df: pd.DataFrame,
    eth_prices_df: pd.DataFrame,
    sol_prices_df: pd.DataFrame,
    output_dir: Path,
    filename: str = "multi_crypto_prices_sentiment_2025.csv"
) -> str:
    """
    Crée le dataset multi-crypto (BTC, ETH, SOL) + Sentiment pour 2025.
    
    Args:
        sentiment_df: DataFrame de sentiment filtré (contient déjà les prix BTC)
        btc_prices_df: DataFrame des prix BTC (pour vérification/remplacement)
        eth_prices_df: DataFrame des prix ETH
        sol_prices_df: DataFrame des prix SOL
        output_dir: Répertoire de sortie
        filename: Nom du fichier de sortie
    
    Returns:
        Chemin du fichier créé
    """
    logger.info("Création du dataset multi-crypto (BTC, ETH, SOL) + Sentiment 2025...")
    
    # Partir du dataset de sentiment comme base (contient déjà prix BTC + sentiment)
    result_df = sentiment_df.copy()
    
    # Renommer les colonnes BTC pour cohérence (Open, High, Low, Close, Volume → Open_BTC, etc.)
    btc_rename_map = {
        'Open': 'Open_BTC',
        'High': 'High_BTC',
        'Low': 'Low_BTC',
        'Close': 'Close_BTC',
        'Volume': 'Volume_BTC'
    }
    
    for old_col, new_col in btc_rename_map.items():
        if old_col in result_df.columns:
            result_df = result_df.rename(columns={old_col: new_col})
    
    # Ajouter return_close_BTC si pas déjà présent
    if 'return_close' in result_df.columns:
        result_df = result_df.rename(columns={'return_close': 'return_close_BTC'})
    elif 'return_close_BTC' not in result_df.columns:
        result_df['return_close_BTC'] = result_df['Close_BTC'].pct_change()
    
    # Joindre les prix ETH
    if not eth_prices_df.empty:
        logger.info("Ajout des prix ETH...")
        result_df = result_df.merge(
            eth_prices_df[['date', f'Open_ETH', f'High_ETH', f'Low_ETH', 
                          f'Close_ETH', f'Volume_ETH', f'return_close_ETH']],
            on='date',
            how='inner'
        )
        logger.info(f"  Prix ETH ajoutés: {len(result_df)} jours après jointure")
    else:
        logger.warning("Prix ETH non disponibles")
    
    # Joindre les prix SOL
    if not sol_prices_df.empty:
        logger.info("Ajout des prix SOL...")
        result_df = result_df.merge(
            sol_prices_df[['date', f'Open_SOL', f'High_SOL', f'Low_SOL', 
                          f'Close_SOL', f'Volume_SOL', f'return_close_SOL']],
            on='date',
            how='inner'
        )
        logger.info(f"  Prix SOL ajoutés: {len(result_df)} jours après jointure")
    else:
        logger.warning("Prix SOL non disponibles")
    
    # Trier par date
    result_df = result_df.sort_values('date').reset_index(drop=True)
    
    # Sauvegarder
    output_path = output_dir / filename
    result_df.to_csv(output_path, index=False)
    
    logger.info(f"Dataset multi-crypto sauvegardé: {output_path}")
    logger.info(f"  Nombre de jours: {len(result_df)}")
    logger.info(f"  Période: {result_df['date'].min().date()} → {result_df['date'].max().date()}")
    logger.info(f"  Colonnes: {len(result_df.columns)}")
    
    return str(output_path)


def verify_datasets(btc_file: str, multi_file: str):
    """
    Effectue des vérifications sur les datasets créés.
    
    Args:
        btc_file: Chemin vers le fichier BTC + Sentiment
        multi_file: Chemin vers le fichier multi-crypto
    """
    logger.info("="*60)
    logger.info("VÉRIFICATIONS FINALES")
    logger.info("="*60)
    
    # Vérifier btc_prices_sentiment_2025.csv
    logger.info(f"\nVérification de {btc_file}:")
    btc_df = pd.read_csv(btc_file)
    btc_df['date'] = pd.to_datetime(btc_df['date'])
    
    logger.info(f"  Nombre de lignes: {len(btc_df)}")
    logger.info(f"  Date min: {btc_df['date'].min().date()}")
    logger.info(f"  Date max: {btc_df['date'].max().date()}")
    logger.info(f"  Colonnes ({len(btc_df.columns)}):")
    for col in btc_df.columns:
        logger.info(f"    - {col}")
    
    # Vérifier multi_crypto_prices_sentiment_2025.csv
    logger.info(f"\nVérification de {multi_file}:")
    multi_df = pd.read_csv(multi_file)
    multi_df['date'] = pd.to_datetime(multi_df['date'])
    
    logger.info(f"  Nombre de lignes: {len(multi_df)}")
    logger.info(f"  Date min: {multi_df['date'].min().date()}")
    logger.info(f"  Date max: {multi_df['date'].max().date()}")
    logger.info(f"  Dates dupliquées: {multi_df['date'].duplicated().sum()}")
    logger.info(f"  Colonnes ({len(multi_df.columns)}):")
    for col in multi_df.columns:
        logger.info(f"    - {col}")


def main():
    """
    Fonction principale de préparation des datasets alignés.
    """
    logger.info("="*60)
    logger.info("PRÉPARATION DES DATASETS ALIGNÉS 2025")
    logger.info("="*60)
    
    # Configuration
    START_DATE = "2025-02-05"
    END_DATE = "2025-08-21"
    OUTPUT_DIR = "data/analysis_2025"
    
    # Chemins des fichiers d'entrée
    SENTIMENT_FILE = "data/gold/bitcoin_sentiment/btc_sentiment_daily.csv"
    BTC_PRICES_FILE = "data/bronze/BTC/historical_prices.csv"
    ETH_PRICES_FILE = "data/bronze/ETH/historical_prices.csv"
    SOL_PRICES_FILE = "data/bronze/SOL/historical_prices.csv"
    
    # 1. Créer le répertoire de sortie
    output_path = create_output_directory(OUTPUT_DIR)
    
    # 2. Charger et filtrer les données de sentiment
    sentiment_df = load_and_filter_sentiment_data(
        SENTIMENT_FILE,
        START_DATE,
        END_DATE
    )
    
    # 3. Charger et filtrer les prix crypto
    logger.info("\nChargement des prix crypto...")
    btc_prices_df = load_and_filter_crypto_prices(
        BTC_PRICES_FILE,
        "BTC",
        START_DATE,
        END_DATE
    )
    eth_prices_df = load_and_filter_crypto_prices(
        ETH_PRICES_FILE,
        "ETH",
        START_DATE,
        END_DATE
    )
    sol_prices_df = load_and_filter_crypto_prices(
        SOL_PRICES_FILE,
        "SOL",
        START_DATE,
        END_DATE
    )
    
    # 4. Créer le dataset BTC + Sentiment
    btc_sentiment_file = create_btc_sentiment_dataset(
        sentiment_df,
        output_path,
        "btc_prices_sentiment_2025.csv"
    )
    
    # 5. Créer le dataset multi-crypto
    multi_crypto_file = create_multi_crypto_dataset(
        sentiment_df,
        btc_prices_df,
        eth_prices_df,
        sol_prices_df,
        output_path,
        "multi_crypto_prices_sentiment_2025.csv"
    )
    
    # 6. Vérifications finales
    verify_datasets(btc_sentiment_file, multi_crypto_file)
    
    # 7. Résumé final
    logger.info("\n" + "="*60)
    logger.info("RÉSUMÉ FINAL")
    logger.info("="*60)
    logger.info(f"\nFichiers créés:")
    logger.info(f"  1. {btc_sentiment_file}")
    logger.info(f"  2. {multi_crypto_file}")
    logger.info(f"\nPériode retenue: {START_DATE} → {END_DATE}")
    logger.info(f"\nNote: sent_mean_global est NaN pour la plupart des jours 2025 (sera traité plus tard)")
    logger.info("\nPréparation terminée avec succès!")


if __name__ == "__main__":
    main()

