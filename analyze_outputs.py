"""
Script simple pour analyser les outputs des scripts de récupération de données.

Ce script analyse :
1. Les fichiers de prix crypto générés par fetch_crypto_data_yfinance.py
2. Le fichier de sentiment Bitcoin généré par prepare_btc_sentiment_data.py
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, Optional


def analyze_crypto_prices(symbol: str, data_dir: str = "data/bronze") -> Optional[pd.DataFrame]:
    """
    Analyse les données de prix pour une cryptomonnaie.
    
    Args:
        symbol: Symbole de la cryptomonnaie (BTC, ETH, SOL)
        data_dir: Répertoire de base des données
    
    Returns:
        DataFrame avec les données ou None si fichier non trouvé
    """
    file_path = Path(data_dir) / symbol / "historical_prices.csv"
    
    if not file_path.exists():
        print(f"Fichier non trouvé: {file_path}")
        return None
    
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"\n{'='*60}")
    print(f"ANALYSE DES PRIX - {symbol}")
    print(f"{'='*60}")
    print(f"Fichier: {file_path}")
    print(f"Nombre de jours: {len(df)}")
    print(f"Période: {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"\nStatistiques des prix:")
    print(f"  Prix d'ouverture - Min: ${df['price_open'].min():.2f}, Max: ${df['price_open'].max():.2f}, Moyenne: ${df['price_open'].mean():.2f}")
    print(f"  Prix de clôture - Min: ${df['price_close'].min():.2f}, Max: ${df['price_close'].max():.2f}, Moyenne: ${df['price_close'].mean():.2f}")
    print(f"  Volume - Min: {df['volume'].min():.0f}, Max: {df['volume'].max():.0f}, Moyenne: {df['volume'].mean():.0f}")
    
    # Calculer les rendements
    df['return'] = df['price_close'].pct_change()
    print(f"\nRendements journaliers:")
    print(f"  Moyenne: {df['return'].mean():.4f} ({df['return'].mean()*100:.2f}%)")
    print(f"  Écart-type: {df['return'].std():.4f} ({df['return'].std()*100:.2f}%)")
    print(f"  Min: {df['return'].min():.4f} ({df['return'].min()*100:.2f}%)")
    print(f"  Max: {df['return'].max():.4f} ({df['return'].max()*100:.2f}%)")
    
    return df


def analyze_bitcoin_sentiment(data_dir: str = "data/gold/bitcoin_sentiment") -> Optional[pd.DataFrame]:
    """
    Analyse les données de sentiment Bitcoin.
    
    Args:
        data_dir: Répertoire contenant le fichier de sentiment
    
    Returns:
        DataFrame avec les données ou None si fichier non trouvé
    """
    file_path = Path(data_dir) / "btc_sentiment_daily.csv"
    
    if not file_path.exists():
        print(f"\nFichier non trouvé: {file_path}")
        return None
    
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"\n{'='*60}")
    print(f"ANALYSE DU SENTIMENT BITCOIN")
    print(f"{'='*60}")
    print(f"Fichier: {file_path}")
    print(f"Nombre de jours: {len(df)}")
    print(f"Période: {df['date'].min().date()} → {df['date'].max().date()}")
    
    # Statistiques de sentiment
    if 'sent_mean_global' in df.columns:
        print(f"\nStatistiques de sentiment:")
        print(f"  Score moyen - Min: {df['sent_mean_global'].min():.4f}, Max: {df['sent_mean_global'].max():.4f}, Moyenne: {df['sent_mean_global'].mean():.4f}")
    
    if 'N_tweets_total' in df.columns:
        print(f"\nStatistiques des tweets:")
        print(f"  Nombre total de tweets - Min: {df['N_tweets_total'].min():.0f}, Max: {df['N_tweets_total'].max():.0f}, Moyenne: {df['N_tweets_total'].mean():.0f}")
    
    if 'pct_positive_global' in df.columns:
        print(f"\nPourcentages de sentiment:")
        print(f"  Positif - Moyenne: {df['pct_positive_global'].mean():.2%}")
        print(f"  Négatif - Moyenne: {df['pct_negative_global'].mean():.2%}")
        print(f"  Neutre - Moyenne: {df['pct_neutral_global'].mean():.2%}")
    
    # Statistiques de prix si présentes
    if 'Close' in df.columns:
        print(f"\nStatistiques des prix (dans le dataset de sentiment):")
        print(f"  Prix de clôture - Min: ${df['Close'].min():.2f}, Max: ${df['Close'].max():.2f}, Moyenne: ${df['Close'].mean():.2f}")
    
    # Corrélation sentiment/prix si disponible
    if 'sent_mean_global' in df.columns and 'return_close' in df.columns:
        correlation = df['sent_mean_global'].corr(df['return_close'])
        print(f"\nCorrélation sentiment/rendement: {correlation:.4f}")
    
    return df


def main():
    """
    Fonction principale qui analyse tous les outputs disponibles.
    """
    print("="*60)
    print("ANALYSE DES OUTPUTS - CRYPTO ET SENTIMENT")
    print("="*60)
    
    # Analyser les prix crypto
    cryptos = ['BTC', 'ETH', 'SOL']
    crypto_data = {}
    
    for symbol in cryptos:
        df = analyze_crypto_prices(symbol)
        if df is not None:
            crypto_data[symbol] = df
    
    # Analyser le sentiment Bitcoin
    sentiment_df = analyze_bitcoin_sentiment()
    
    # Résumé final
    print(f"\n{'='*60}")
    print("RÉSUMÉ")
    print(f"{'='*60}")
    print(f"Fichiers de prix analysés: {len(crypto_data)}")
    for symbol in crypto_data.keys():
        print(f"  - {symbol}: {len(crypto_data[symbol])} jours")
    
    if sentiment_df is not None:
        print(f"Fichier de sentiment analysé: {len(sentiment_df)} jours")
    else:
        print("Fichier de sentiment: non trouvé")
    
    print("\nAnalyse terminée!")


if __name__ == "__main__":
    main()

