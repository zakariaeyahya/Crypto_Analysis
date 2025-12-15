"""
Script d'analyse de corrélation entre les sentiments des posts et les prix ETH/BTC
Utilise le logging pour la traçabilité
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"correlation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Chemins des fichiers
DATA_DIR = Path(__file__).parent.parent / "data" / "silver" / "aligned_datasets"
ETH_FILE = DATA_DIR / "eth_prices_aligned.csv"
BTC_FILE = DATA_DIR / "btc_prices_aligned.csv"
SENTIMENT_FILE = DATA_DIR / "crypto_sent_aligned.csv"

# Dossier de sortie pour les résultats
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_and_prepare_data():
    """Charge et prépare les données pour l'analyse de corrélation"""
    logger.info("=" * 70)
    logger.info("CHARGEMENT ET PRÉPARATION DES DONNÉES")
    logger.info("=" * 70)
    
    # Charger les datasets
    eth_df = pd.read_csv(ETH_FILE)
    btc_df = pd.read_csv(BTC_FILE)
    sent_df = pd.read_csv(SENTIMENT_FILE)
    
    logger.info(f"✓ ETH chargé: {len(eth_df)} lignes")
    logger.info(f"✓ BTC chargé: {len(btc_df)} lignes")
    logger.info(f"✓ Sentiment chargé: {len(sent_df)} lignes")
    
    # Préparer les dates
    eth_df['date'] = pd.to_datetime(eth_df['date']).dt.date
    btc_df['date'] = pd.to_datetime(btc_df['date']).dt.date
    sent_df['date'] = pd.to_datetime(sent_df['created_at']).dt.date
    
    return eth_df, btc_df, sent_df


def aggregate_daily_sentiment(sent_df):
    """Agrège les sentiments par jour"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("AGRÉGATION DES SENTIMENTS PAR JOUR")
    logger.info("=" * 70)
    
    # Convertir les sentiments en valeurs numériques
    sentiment_mapping = {
        'extremely_negative': -2,
        'negative': -1,
        'neutral': 0,
        'positive': 1,
        'extremely_positive': 2
    }
    sent_df['sentiment_numeric'] = sent_df['sentiment'].map(sentiment_mapping)
    
    # Agrégation par jour
    daily_sentiment = sent_df.groupby('date').agg({
        'score': ['mean', 'std', 'count'],
        'sentiment_numeric': ['mean', 'std'],
        'sentiment': lambda x: (x == 'positive').sum() + (x == 'extremely_positive').sum(),  # count positif
    }).reset_index()
    
    # Aplatir les colonnes multi-niveaux
    daily_sentiment.columns = [
        'date', 
        'score_mean', 'score_std', 'post_count',
        'sentiment_mean', 'sentiment_std',
        'positive_count'
    ]
    
    # Calculer le ratio de posts positifs
    daily_sentiment['positive_ratio'] = daily_sentiment['positive_count'] / daily_sentiment['post_count']
    
    # Calculer les posts négatifs
    daily_negative = sent_df.groupby('date')['sentiment'].apply(
        lambda x: (x == 'negative').sum() + (x == 'extremely_negative').sum()
    ).reset_index()
    daily_negative.columns = ['date', 'negative_count']
    daily_sentiment = daily_sentiment.merge(daily_negative, on='date')
    daily_sentiment['negative_ratio'] = daily_sentiment['negative_count'] / daily_sentiment['post_count']
    
    # Ratio positif/négatif
    daily_sentiment['sentiment_ratio'] = daily_sentiment['positive_count'] / (daily_sentiment['negative_count'] + 1)
    
    logger.info(f"✓ {len(daily_sentiment)} jours agrégés")
    logger.info(f"Score moyen global: {daily_sentiment['score_mean'].mean():.4f}")
    logger.info(f"Posts par jour - Min: {daily_sentiment['post_count'].min()} | Max: {daily_sentiment['post_count'].max()} | Moyenne: {daily_sentiment['post_count'].mean():.1f}")
    
    return daily_sentiment


def prepare_price_features(df, crypto_name):
    """Prépare les features de prix pour l'analyse"""
    df = df.copy()
    
    # Variation journalière
    df['daily_return'] = ((df['price_close'] - df['price_open']) / df['price_open']) * 100
    
    # Variation par rapport au jour précédent
    df['price_change'] = df['price_close'].pct_change() * 100
    
    # Volatilité (écart entre high et low approximé par open/close)
    df['volatility'] = abs(df['price_close'] - df['price_open']) / df['price_open'] * 100
    
    # Direction du prix (1 = hausse, 0 = baisse)
    df['price_direction'] = (df['daily_return'] > 0).astype(int)
    
    # Renommer les colonnes avec le préfixe crypto
    rename_cols = {
        'price_open': f'{crypto_name}_open',
        'price_close': f'{crypto_name}_close',
        'volume': f'{crypto_name}_volume',
        'daily_return': f'{crypto_name}_daily_return',
        'price_change': f'{crypto_name}_price_change',
        'volatility': f'{crypto_name}_volatility',
        'price_direction': f'{crypto_name}_direction'
    }
    df = df.rename(columns=rename_cols)
    
    return df[['date'] + list(rename_cols.values())]


def merge_datasets(daily_sentiment, eth_df, btc_df):
    """Fusionne tous les datasets"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("FUSION DES DATASETS")
    logger.info("=" * 70)
    
    # Préparer les features de prix
    eth_features = prepare_price_features(eth_df, 'ETH')
    btc_features = prepare_price_features(btc_df, 'BTC')
    
    # Fusion
    merged = daily_sentiment.merge(btc_features, on='date', how='inner')
    logger.info(f"Après fusion avec BTC: {len(merged)} jours")
    
    merged_with_eth = merged.merge(eth_features, on='date', how='inner')
    logger.info(f"Après fusion avec ETH: {len(merged_with_eth)} jours")
    
    logger.info(f"Période: {merged_with_eth['date'].min()} → {merged_with_eth['date'].max()}")
    
    return merged_with_eth


def calculate_correlations(df):
    """Calcule les corrélations entre sentiment et prix"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("ANALYSE DES CORRÉLATIONS")
    logger.info("=" * 70)
    
    # Variables de sentiment
    sentiment_vars = ['score_mean', 'sentiment_mean', 'positive_ratio', 'negative_ratio', 'sentiment_ratio']
    
    # Variables de prix
    price_vars = [
        'BTC_daily_return', 'BTC_price_change', 'BTC_volatility', 'BTC_volume',
        'ETH_daily_return', 'ETH_price_change', 'ETH_volatility', 'ETH_volume'
    ]
    
    results = []
    
    logger.info("")
    logger.info("--- Corrélations de Pearson ---")
    
    for sent_var in sentiment_vars:
        for price_var in price_vars:
            if sent_var in df.columns and price_var in df.columns:
                # Supprimer les NaN
                valid = df[[sent_var, price_var]].dropna()
                if len(valid) > 10:
                    corr, p_value = stats.pearsonr(valid[sent_var], valid[price_var])
                    results.append({
                        'sentiment_var': sent_var,
                        'price_var': price_var,
                        'correlation': corr,
                        'p_value': p_value,
                        'significant': p_value < 0.05,
                        'n_samples': len(valid)
                    })
    
    results_df = pd.DataFrame(results)
    
    # Afficher les corrélations significatives
    significant = results_df[results_df['significant']].sort_values('correlation', key=abs, ascending=False)
    
    if len(significant) > 0:
        logger.info(f"\n{len(significant)} corrélations significatives (p < 0.05):")
        for _, row in significant.head(15).iterrows():
            strength = "forte" if abs(row['correlation']) > 0.5 else "modérée" if abs(row['correlation']) > 0.3 else "faible"
            direction = "positive" if row['correlation'] > 0 else "négative"
            logger.info(f"  {row['sentiment_var']} ↔ {row['price_var']}: r={row['correlation']:.4f} (p={row['p_value']:.4f}) [{strength}, {direction}]")
    else:
        logger.info("Aucune corrélation significative trouvée (p < 0.05)")
    
    # Top corrélations par crypto
    logger.info("")
    logger.info("--- Top Corrélations par Crypto ---")
    
    for crypto in ['BTC', 'ETH']:
        crypto_results = results_df[results_df['price_var'].str.contains(crypto)]
        if len(crypto_results) > 0:
            top = crypto_results.nlargest(3, 'correlation', keep='first')
            logger.info(f"\n{crypto} - Meilleures corrélations positives:")
            for _, row in top.iterrows():
                logger.info(f"  {row['sentiment_var']} ↔ {row['price_var']}: r={row['correlation']:.4f}")
            
            bottom = crypto_results.nsmallest(3, 'correlation', keep='first')
            logger.info(f"{crypto} - Meilleures corrélations négatives:")
            for _, row in bottom.iterrows():
                logger.info(f"  {row['sentiment_var']} ↔ {row['price_var']}: r={row['correlation']:.4f}")
    
    return results_df


def calculate_lagged_correlations(df, max_lag=7):
    """Calcule les corrélations avec décalage temporel (le sentiment prédit-il le prix?)"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("CORRÉLATIONS AVEC DÉCALAGE TEMPOREL (LAG)")
    logger.info("=" * 70)
    logger.info("(Le sentiment d'aujourd'hui prédit-il le prix de demain?)")
    
    df = df.copy()
    df = df.sort_values('date').reset_index(drop=True)
    
    sentiment_vars = ['score_mean', 'sentiment_mean', 'positive_ratio']
    price_vars = ['BTC_daily_return', 'ETH_daily_return']
    
    lag_results = []
    
    for lag in range(1, max_lag + 1):
        for sent_var in sentiment_vars:
            for price_var in price_vars:
                if sent_var in df.columns and price_var in df.columns:
                    # Décaler le prix de 'lag' jours (sentiment aujourd'hui vs prix dans 'lag' jours)
                    df_lagged = df.copy()
                    df_lagged['price_future'] = df_lagged[price_var].shift(-lag)
                    
                    valid = df_lagged[[sent_var, 'price_future']].dropna()
                    if len(valid) > 10:
                        corr, p_value = stats.pearsonr(valid[sent_var], valid['price_future'])
                        lag_results.append({
                            'lag_days': lag,
                            'sentiment_var': sent_var,
                            'price_var': price_var,
                            'correlation': corr,
                            'p_value': p_value,
                            'significant': p_value < 0.05
                        })
    
    lag_df = pd.DataFrame(lag_results)
    
    # Meilleurs lags prédictifs
    significant_lags = lag_df[lag_df['significant']].sort_values('correlation', key=abs, ascending=False)
    
    if len(significant_lags) > 0:
        logger.info(f"\nCorrélations significatives avec décalage temporel:")
        for _, row in significant_lags.head(10).iterrows():
            logger.info(f"  {row['sentiment_var']} → {row['price_var']} (J+{row['lag_days']}): r={row['correlation']:.4f} (p={row['p_value']:.4f})")
    else:
        logger.info("Aucune corrélation prédictive significative trouvée")
    
    # Analyse par lag
    logger.info("")
    logger.info("--- Corrélation moyenne par Lag ---")
    avg_by_lag = lag_df.groupby('lag_days')['correlation'].mean()
    for lag, avg_corr in avg_by_lag.items():
        logger.info(f"  J+{lag}: corrélation moyenne = {avg_corr:.4f}")
    
    return lag_df


def analyze_sentiment_price_direction(df):
    """Analyse si le sentiment prédit la direction du prix"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("ANALYSE SENTIMENT vs DIRECTION DU PRIX")
    logger.info("=" * 70)
    
    df = df.copy()
    
    # Créer des catégories de sentiment
    df['sentiment_category'] = pd.cut(df['score_mean'], 
                                       bins=[-1, -0.1, 0.1, 1], 
                                       labels=['Négatif', 'Neutre', 'Positif'])
    
    for crypto in ['BTC', 'ETH']:
        direction_col = f'{crypto}_direction'
        if direction_col in df.columns:
            logger.info(f"\n--- {crypto} ---")
            
            # Crosstab sentiment vs direction
            crosstab = pd.crosstab(df['sentiment_category'], 
                                   df[direction_col], 
                                   margins=True, 
                                   normalize='index')
            
            logger.info("Probabilité de hausse selon le sentiment:")
            for cat in ['Négatif', 'Neutre', 'Positif']:
                if cat in crosstab.index:
                    prob_up = crosstab.loc[cat, 1] * 100 if 1 in crosstab.columns else 0
                    logger.info(f"  Sentiment {cat}: {prob_up:.1f}% de jours en hausse")
            
            # Test Chi2
            contingency = pd.crosstab(df['sentiment_category'].dropna(), 
                                      df[direction_col].dropna())
            if contingency.shape[0] > 1 and contingency.shape[1] > 1:
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
                logger.info(f"  Test Chi²: χ²={chi2:.2f}, p={p_value:.4f} ({'Significatif' if p_value < 0.05 else 'Non significatif'})")


def calculate_spearman_correlations(df):
    """Calcule les corrélations de Spearman (rangs)"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("CORRÉLATIONS DE SPEARMAN (RANGS)")
    logger.info("=" * 70)
    
    sentiment_vars = ['score_mean', 'sentiment_mean', 'positive_ratio', 'negative_ratio']
    price_vars = ['BTC_daily_return', 'BTC_volume', 'ETH_daily_return', 'ETH_volume']
    
    results = []
    
    for sent_var in sentiment_vars:
        for price_var in price_vars:
            if sent_var in df.columns and price_var in df.columns:
                valid = df[[sent_var, price_var]].dropna()
                if len(valid) > 10:
                    corr, p_value = stats.spearmanr(valid[sent_var], valid[price_var])
                    results.append({
                        'sentiment_var': sent_var,
                        'price_var': price_var,
                        'spearman_corr': corr,
                        'p_value': p_value,
                        'significant': p_value < 0.05
                    })
    
    results_df = pd.DataFrame(results)
    significant = results_df[results_df['significant']].sort_values('spearman_corr', key=abs, ascending=False)
    
    if len(significant) > 0:
        logger.info("Corrélations de Spearman significatives:")
        for _, row in significant.head(10).iterrows():
            logger.info(f"  {row['sentiment_var']} ↔ {row['price_var']}: ρ={row['spearman_corr']:.4f} (p={row['p_value']:.4f})")
    else:
        logger.info("Aucune corrélation de Spearman significative")
    
    return results_df


def generate_correlation_summary(pearson_df, spearman_df, lag_df, df):
    """Génère un résumé des corrélations"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("RÉSUMÉ DE L'ANALYSE DE CORRÉLATION")
    logger.info("=" * 70)
    
    logger.info(f"\n📊 Période analysée: {df['date'].min()} → {df['date'].max()} ({len(df)} jours)")
    logger.info(f"📝 Total posts analysés: {df['post_count'].sum():,}")
    
    # Résumé Pearson
    sig_pearson = pearson_df[pearson_df['significant']]
    logger.info(f"\n--- Pearson ---")
    logger.info(f"Corrélations significatives: {len(sig_pearson)}/{len(pearson_df)}")
    if len(sig_pearson) > 0:
        best = sig_pearson.loc[sig_pearson['correlation'].abs().idxmax()]
        logger.info(f"Plus forte: {best['sentiment_var']} ↔ {best['price_var']} (r={best['correlation']:.4f})")
    
    # Résumé Spearman
    sig_spearman = spearman_df[spearman_df['significant']]
    logger.info(f"\n--- Spearman ---")
    logger.info(f"Corrélations significatives: {len(sig_spearman)}/{len(spearman_df)}")
    
    # Résumé Lag
    sig_lag = lag_df[lag_df['significant']]
    logger.info(f"\n--- Corrélations Prédictives (Lag) ---")
    logger.info(f"Corrélations significatives: {len(sig_lag)}/{len(lag_df)}")
    if len(sig_lag) > 0:
        best_lag = sig_lag.loc[sig_lag['correlation'].abs().idxmax()]
        logger.info(f"Meilleur lag prédictif: {best_lag['sentiment_var']} → {best_lag['price_var']} J+{best_lag['lag_days']} (r={best_lag['correlation']:.4f})")
    
    # Conclusions
    logger.info("")
    logger.info("=" * 70)
    logger.info("CONCLUSIONS")
    logger.info("=" * 70)
    
    avg_btc_corr = pearson_df[pearson_df['price_var'].str.contains('BTC')]['correlation'].abs().mean()
    avg_eth_corr = pearson_df[pearson_df['price_var'].str.contains('ETH')]['correlation'].abs().mean()
    
    logger.info(f"• Corrélation moyenne avec BTC: {avg_btc_corr:.4f}")
    logger.info(f"• Corrélation moyenne avec ETH: {avg_eth_corr:.4f}")
    
    if avg_btc_corr > 0.3 or avg_eth_corr > 0.3:
        logger.info("• ✓ Relation modérée à forte entre sentiment et prix détectée")
    elif avg_btc_corr > 0.1 or avg_eth_corr > 0.1:
        logger.info("• ~ Relation faible entre sentiment et prix détectée")
    else:
        logger.info("• ✗ Pas de relation significative entre sentiment et prix")
    
    logger.info("")
    logger.info("Analyse terminée avec succès ✓")
    logger.info(f"Logs sauvegardés dans: {LOG_DIR}")


def save_results(pearson_df, spearman_df, lag_df, merged_df):
    """Sauvegarde les résultats dans des fichiers CSV"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("SAUVEGARDE DES RÉSULTATS")
    logger.info("=" * 70)
    
    # Sauvegarder les corrélations
    pearson_df.to_csv(OUTPUT_DIR / "correlations_pearson.csv", index=False)
    logger.info(f"✓ Corrélations Pearson: {OUTPUT_DIR / 'correlations_pearson.csv'}")
    
    spearman_df.to_csv(OUTPUT_DIR / "correlations_spearman.csv", index=False)
    logger.info(f"✓ Corrélations Spearman: {OUTPUT_DIR / 'correlations_spearman.csv'}")
    
    lag_df.to_csv(OUTPUT_DIR / "correlations_lag.csv", index=False)
    logger.info(f"✓ Corrélations Lag: {OUTPUT_DIR / 'correlations_lag.csv'}")
    
    # Sauvegarder le dataset fusionné
    merged_df.to_csv(OUTPUT_DIR / "merged_sentiment_prices.csv", index=False)
    logger.info(f"✓ Dataset fusionné: {OUTPUT_DIR / 'merged_sentiment_prices.csv'}")


def main():
    """Fonction principale"""
    logger.info("=" * 70)
    logger.info("ANALYSE DE CORRÉLATION: SENTIMENT vs PRIX CRYPTO (ETH/BTC)")
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # Charger les données
    eth_df, btc_df, sent_df = load_and_prepare_data()
    
    # Agréger les sentiments par jour
    daily_sentiment = aggregate_daily_sentiment(sent_df)
    
    # Fusionner les datasets
    merged_df = merge_datasets(daily_sentiment, eth_df, btc_df)
    
    # Calculer les corrélations de Pearson
    pearson_df = calculate_correlations(merged_df)
    
    # Calculer les corrélations de Spearman
    spearman_df = calculate_spearman_correlations(merged_df)
    
    # Analyser sentiment vs direction du prix
    analyze_sentiment_price_direction(merged_df)
    
    # Calculer les corrélations avec lag
    lag_df = calculate_lagged_correlations(merged_df)
    
    # Générer le résumé
    generate_correlation_summary(pearson_df, spearman_df, lag_df, merged_df)
    
    # Sauvegarder les résultats
    save_results(pearson_df, spearman_df, lag_df, merged_df)


if __name__ == "__main__":
    main()



