"""
Dashboard de visualisation des corrélations Sentiment vs Prix Crypto (ETH/BTC)
Génère des graphiques et un dashboard HTML interactif
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
        logging.FileHandler(LOG_DIR / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Chemins
DATA_DIR = Path(__file__).parent.parent / "data" / "silver" / "aligned_datasets"
OUTPUT_DIR = Path(__file__).parent / "outputs"
PLOTS_DIR = OUTPUT_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Style des graphiques
plt.style.use('seaborn-v0_8-darkgrid')
COLORS = {
    'btc': '#F7931A',      # Orange Bitcoin
    'eth': '#627EEA',      # Bleu Ethereum
    'positive': '#00C853', # Vert
    'negative': '#FF1744', # Rouge
    'neutral': '#78909C',  # Gris
    'primary': '#1E88E5',  # Bleu primaire
    'secondary': '#7C4DFF' # Violet
}


def load_data():
    """Charge les données"""
    logger.info("=" * 70)
    logger.info("CHARGEMENT DES DONNÉES")
    logger.info("=" * 70)
    
    # Charger le dataset fusionné s'il existe
    merged_file = OUTPUT_DIR / "merged_sentiment_prices.csv"
    if merged_file.exists():
        df = pd.read_csv(merged_file)
        df['date'] = pd.to_datetime(df['date'])
        logger.info(f"✓ Dataset fusionné chargé: {len(df)} lignes")
        return df
    
    # Sinon, charger et fusionner les datasets
    logger.info("Dataset fusionné non trouvé, création en cours...")
    
    eth_df = pd.read_csv(DATA_DIR / "eth_prices_aligned.csv")
    btc_df = pd.read_csv(DATA_DIR / "btc_prices_aligned.csv")
    sent_df = pd.read_csv(DATA_DIR / "crypto_sent_aligned.csv")
    
    # Préparer les données
    eth_df['date'] = pd.to_datetime(eth_df['date']).dt.date
    btc_df['date'] = pd.to_datetime(btc_df['date']).dt.date
    sent_df['date'] = pd.to_datetime(sent_df['created_at']).dt.date
    
    # Mapping sentiment
    sentiment_mapping = {
        'extremely_negative': -2, 'negative': -1, 'neutral': 0,
        'positive': 1, 'extremely_positive': 2
    }
    sent_df['sentiment_numeric'] = sent_df['sentiment'].map(sentiment_mapping)
    
    # Agrégation par jour
    daily = sent_df.groupby('date').agg({
        'score': ['mean', 'std', 'count'],
        'sentiment_numeric': 'mean'
    }).reset_index()
    daily.columns = ['date', 'score_mean', 'score_std', 'post_count', 'sentiment_mean']
    
    # Préparer ETH
    eth_df['ETH_daily_return'] = ((eth_df['price_close'] - eth_df['price_open']) / eth_df['price_open']) * 100
    eth_df = eth_df.rename(columns={
        'price_close': 'ETH_close', 'price_open': 'ETH_open', 'volume': 'ETH_volume'
    })[['date', 'ETH_open', 'ETH_close', 'ETH_volume', 'ETH_daily_return']]
    
    # Préparer BTC
    btc_df['BTC_daily_return'] = ((btc_df['price_close'] - btc_df['price_open']) / btc_df['price_open']) * 100
    btc_df = btc_df.rename(columns={
        'price_close': 'BTC_close', 'price_open': 'BTC_open', 'volume': 'BTC_volume'
    })[['date', 'BTC_open', 'BTC_close', 'BTC_volume', 'BTC_daily_return']]
    
    # Fusion
    df = daily.merge(btc_df, on='date', how='inner')
    df = df.merge(eth_df, on='date', how='inner')
    df['date'] = pd.to_datetime(df['date'])
    
    logger.info(f"✓ Dataset créé: {len(df)} lignes")
    return df


def plot_correlation_heatmap(df):
    """Génère une heatmap des corrélations"""
    logger.info("Génération de la heatmap des corrélations...")
    
    # Sélectionner les colonnes numériques pertinentes
    cols = ['score_mean', 'sentiment_mean', 'post_count',
            'BTC_daily_return', 'BTC_close', 'BTC_volume',
            'ETH_daily_return', 'ETH_close', 'ETH_volume']
    
    cols_available = [c for c in cols if c in df.columns]
    corr_matrix = df[cols_available].corr()
    
    # Renommer pour l'affichage
    rename_map = {
        'score_mean': 'Score Sentiment',
        'sentiment_mean': 'Sentiment Moyen',
        'post_count': 'Nb Posts',
        'BTC_daily_return': 'BTC Retour %',
        'BTC_close': 'BTC Prix',
        'BTC_volume': 'BTC Volume',
        'ETH_daily_return': 'ETH Retour %',
        'ETH_close': 'ETH Prix',
        'ETH_volume': 'ETH Volume'
    }
    corr_matrix = corr_matrix.rename(index=rename_map, columns=rename_map)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Créer la heatmap
    im = ax.imshow(corr_matrix, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
    
    # Ajouter les labels
    ax.set_xticks(range(len(corr_matrix.columns)))
    ax.set_yticks(range(len(corr_matrix.index)))
    ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right', fontsize=10)
    ax.set_yticklabels(corr_matrix.index, fontsize=10)
    
    # Ajouter les valeurs dans les cellules
    for i in range(len(corr_matrix.index)):
        for j in range(len(corr_matrix.columns)):
            val = corr_matrix.iloc[i, j]
            color = 'white' if abs(val) > 0.5 else 'black'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', color=color, fontsize=9)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Corrélation', fontsize=12)
    
    ax.set_title('Matrice de Corrélation: Sentiment vs Prix Crypto', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'correlation_heatmap.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"✓ Heatmap sauvegardée: {PLOTS_DIR / 'correlation_heatmap.png'}")


def plot_time_series(df):
    """Génère les graphiques de séries temporelles"""
    logger.info("Génération des séries temporelles...")
    
    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
    
    # 1. Score de sentiment
    ax1 = axes[0]
    ax1.fill_between(df['date'], df['score_mean'], alpha=0.3, color=COLORS['primary'])
    ax1.plot(df['date'], df['score_mean'], color=COLORS['primary'], linewidth=1.5, label='Score Sentiment')
    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax1.set_ylabel('Score Sentiment', fontsize=11)
    ax1.set_title('Évolution Temporelle: Sentiment vs Prix Crypto', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.set_ylim(-0.5, 0.5)
    
    # 2. Prix BTC
    ax2 = axes[1]
    ax2.plot(df['date'], df['BTC_close'], color=COLORS['btc'], linewidth=2, label='BTC Prix')
    ax2.fill_between(df['date'], df['BTC_close'], alpha=0.2, color=COLORS['btc'])
    ax2.set_ylabel('BTC Prix ($)', fontsize=11)
    ax2.legend(loc='upper right')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # 3. Prix ETH
    ax3 = axes[2]
    ax3.plot(df['date'], df['ETH_close'], color=COLORS['eth'], linewidth=2, label='ETH Prix')
    ax3.fill_between(df['date'], df['ETH_close'], alpha=0.2, color=COLORS['eth'])
    ax3.set_ylabel('ETH Prix ($)', fontsize=11)
    ax3.legend(loc='upper right')
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # 4. Nombre de posts
    ax4 = axes[3]
    ax4.bar(df['date'], df['post_count'], color=COLORS['secondary'], alpha=0.7, label='Nombre de Posts')
    ax4.set_ylabel('Nombre de Posts', fontsize=11)
    ax4.set_xlabel('Date', fontsize=11)
    ax4.legend(loc='upper right')
    
    # Format des dates
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax4.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'time_series.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"✓ Séries temporelles sauvegardées: {PLOTS_DIR / 'time_series.png'}")


def plot_scatter_correlations(df):
    """Génère les scatter plots de corrélation"""
    logger.info("Génération des scatter plots...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 1. Score Sentiment vs BTC Return
    ax1 = axes[0, 0]
    ax1.scatter(df['score_mean'], df['BTC_daily_return'], alpha=0.6, c=COLORS['btc'], edgecolors='white', s=60)
    # Ligne de régression
    z = np.polyfit(df['score_mean'].dropna(), df['BTC_daily_return'].dropna(), 1)
    p = np.poly1d(z)
    x_line = np.linspace(df['score_mean'].min(), df['score_mean'].max(), 100)
    ax1.plot(x_line, p(x_line), color='red', linestyle='--', linewidth=2, label=f'Régression (r={df["score_mean"].corr(df["BTC_daily_return"]):.3f})')
    ax1.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax1.axvline(x=0, color='gray', linestyle='-', alpha=0.3)
    ax1.set_xlabel('Score Sentiment Moyen', fontsize=11)
    ax1.set_ylabel('BTC Retour Journalier (%)', fontsize=11)
    ax1.set_title('Sentiment vs Retour BTC', fontsize=12, fontweight='bold')
    ax1.legend()
    
    # 2. Score Sentiment vs ETH Return
    ax2 = axes[0, 1]
    ax2.scatter(df['score_mean'], df['ETH_daily_return'], alpha=0.6, c=COLORS['eth'], edgecolors='white', s=60)
    z = np.polyfit(df['score_mean'].dropna(), df['ETH_daily_return'].dropna(), 1)
    p = np.poly1d(z)
    ax2.plot(x_line, p(x_line), color='red', linestyle='--', linewidth=2, label=f'Régression (r={df["score_mean"].corr(df["ETH_daily_return"]):.3f})')
    ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax2.axvline(x=0, color='gray', linestyle='-', alpha=0.3)
    ax2.set_xlabel('Score Sentiment Moyen', fontsize=11)
    ax2.set_ylabel('ETH Retour Journalier (%)', fontsize=11)
    ax2.set_title('Sentiment vs Retour ETH', fontsize=12, fontweight='bold')
    ax2.legend()
    
    # 3. Nombre de posts vs BTC Volume
    ax3 = axes[1, 0]
    ax3.scatter(df['post_count'], df['BTC_volume'], alpha=0.6, c=COLORS['btc'], edgecolors='white', s=60)
    ax3.set_xlabel('Nombre de Posts', fontsize=11)
    ax3.set_ylabel('BTC Volume', fontsize=11)
    ax3.set_title('Activité Social vs Volume BTC', fontsize=12, fontweight='bold')
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e9:.1f}B'))
    
    # 4. Sentiment vs Prix BTC (normalisé)
    ax4 = axes[1, 1]
    # Normaliser les deux séries
    btc_norm = (df['BTC_close'] - df['BTC_close'].min()) / (df['BTC_close'].max() - df['BTC_close'].min())
    sent_norm = (df['score_mean'] - df['score_mean'].min()) / (df['score_mean'].max() - df['score_mean'].min())
    ax4.plot(df['date'], sent_norm, label='Sentiment (normalisé)', color=COLORS['primary'], linewidth=2)
    ax4.plot(df['date'], btc_norm, label='BTC Prix (normalisé)', color=COLORS['btc'], linewidth=2)
    ax4.set_xlabel('Date', fontsize=11)
    ax4.set_ylabel('Valeur Normalisée', fontsize=11)
    ax4.set_title('Comparaison Sentiment vs BTC (Normalisés)', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'scatter_correlations.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"✓ Scatter plots sauvegardés: {PLOTS_DIR / 'scatter_correlations.png'}")


def plot_sentiment_distribution(df):
    """Génère la distribution du sentiment"""
    logger.info("Génération de la distribution du sentiment...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 1. Distribution des scores
    ax1 = axes[0]
    ax1.hist(df['score_mean'], bins=30, color=COLORS['primary'], alpha=0.7, edgecolor='white')
    ax1.axvline(df['score_mean'].mean(), color='red', linestyle='--', linewidth=2, label=f'Moyenne: {df["score_mean"].mean():.3f}')
    ax1.axvline(0, color='gray', linestyle='-', linewidth=1)
    ax1.set_xlabel('Score Sentiment Moyen', fontsize=11)
    ax1.set_ylabel('Fréquence', fontsize=11)
    ax1.set_title('Distribution du Score Sentiment', fontsize=12, fontweight='bold')
    ax1.legend()
    
    # 2. Boxplot par direction du prix BTC
    ax2 = axes[1]
    df['BTC_direction'] = np.where(df['BTC_daily_return'] > 0, 'Hausse', 'Baisse')
    
    hausse_data = df[df['BTC_direction'] == 'Hausse']['score_mean']
    baisse_data = df[df['BTC_direction'] == 'Baisse']['score_mean']
    
    bp = ax2.boxplot([baisse_data, hausse_data], 
                     labels=['BTC Baisse', 'BTC Hausse'],
                     patch_artist=True)
    bp['boxes'][0].set_facecolor(COLORS['negative'])
    bp['boxes'][1].set_facecolor(COLORS['positive'])
    bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][1].set_alpha(0.7)
    
    ax2.set_ylabel('Score Sentiment', fontsize=11)
    ax2.set_title('Sentiment selon Direction BTC', fontsize=12, fontweight='bold')
    
    # Ajouter les moyennes
    ax2.scatter([1, 2], [baisse_data.mean(), hausse_data.mean()], 
                color='black', marker='D', s=50, zorder=5, label='Moyenne')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'sentiment_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"✓ Distribution sauvegardée: {PLOTS_DIR / 'sentiment_distribution.png'}")


def plot_lag_analysis(df):
    """Analyse avec décalage temporel"""
    logger.info("Génération de l'analyse des lags...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    lags = range(-7, 8)
    btc_corrs = []
    eth_corrs = []
    
    for lag in lags:
        if lag < 0:
            # Sentiment décalé vers le passé (prix prédit sentiment)
            shifted = df['BTC_daily_return'].shift(lag)
        else:
            # Sentiment décalé vers le futur (sentiment prédit prix)
            shifted = df['BTC_daily_return'].shift(-lag)
        
        valid = pd.DataFrame({'sent': df['score_mean'], 'price': shifted}).dropna()
        if len(valid) > 10:
            corr, _ = stats.pearsonr(valid['sent'], valid['price'])
            btc_corrs.append(corr)
        else:
            btc_corrs.append(0)
    
    for lag in lags:
        if lag < 0:
            shifted = df['ETH_daily_return'].shift(lag)
        else:
            shifted = df['ETH_daily_return'].shift(-lag)
        
        valid = pd.DataFrame({'sent': df['score_mean'], 'price': shifted}).dropna()
        if len(valid) > 10:
            corr, _ = stats.pearsonr(valid['sent'], valid['price'])
            eth_corrs.append(corr)
        else:
            eth_corrs.append(0)
    
    # BTC Lag
    ax1 = axes[0]
    bars = ax1.bar(lags, btc_corrs, color=[COLORS['positive'] if c > 0 else COLORS['negative'] for c in btc_corrs], alpha=0.7)
    ax1.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
    ax1.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    ax1.set_xlabel('Lag (jours)', fontsize=11)
    ax1.set_ylabel('Corrélation', fontsize=11)
    ax1.set_title('Corrélation Sentiment-BTC par Lag', fontsize=12, fontweight='bold')
    ax1.set_xticks(list(lags))
    
    # ETH Lag
    ax2 = axes[1]
    bars = ax2.bar(lags, eth_corrs, color=[COLORS['positive'] if c > 0 else COLORS['negative'] for c in eth_corrs], alpha=0.7)
    ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
    ax2.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Lag (jours)', fontsize=11)
    ax2.set_ylabel('Corrélation', fontsize=11)
    ax2.set_title('Corrélation Sentiment-ETH par Lag', fontsize=12, fontweight='bold')
    ax2.set_xticks(list(lags))
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'lag_analysis.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"✓ Analyse lag sauvegardée: {PLOTS_DIR / 'lag_analysis.png'}")


def generate_html_dashboard(df):
    """Génère un dashboard HTML interactif"""
    logger.info("Génération du dashboard HTML...")
    
    # Calculer les statistiques
    corr_btc = df['score_mean'].corr(df['BTC_daily_return'])
    corr_eth = df['score_mean'].corr(df['ETH_daily_return'])
    
    # Probabilités
    df['BTC_up'] = df['BTC_daily_return'] > 0
    df['ETH_up'] = df['ETH_daily_return'] > 0
    df['sent_positive'] = df['score_mean'] > 0.1
    
    prob_btc_up_sent_pos = df[df['sent_positive']]['BTC_up'].mean() * 100
    prob_eth_up_sent_pos = df[df['sent_positive']]['ETH_up'].mean() * 100
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Corrélation Sentiment-Crypto</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e8e8e8;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            padding: 30px 0;
            margin-bottom: 30px;
        }}
        
        h1 {{
            font-size: 2.5em;
            background: linear-gradient(90deg, #F7931A, #627EEA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #8892b0;
            font-size: 1.1em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}
        
        .stat-card.btc {{
            border-left: 4px solid #F7931A;
        }}
        
        .stat-card.eth {{
            border-left: 4px solid #627EEA;
        }}
        
        .stat-card.sentiment {{
            border-left: 4px solid #00C853;
        }}
        
        .stat-card.correlation {{
            border-left: 4px solid #7C4DFF;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #8892b0;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-value.btc {{ color: #F7931A; }}
        .stat-value.eth {{ color: #627EEA; }}
        .stat-value.positive {{ color: #00C853; }}
        .stat-value.negative {{ color: #FF1744; }}
        .stat-value.neutral {{ color: #78909C; }}
        
        .stat-detail {{
            font-size: 0.85em;
            color: #8892b0;
        }}
        
        .charts-section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 20px;
        }}
        
        .chart-card {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .chart-card img {{
            width: 100%;
            border-radius: 10px;
        }}
        
        .chart-title {{
            font-size: 1.1em;
            margin-bottom: 15px;
            color: #e8e8e8;
        }}
        
        .insights-section {{
            background: rgba(124, 77, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(124, 77, 255, 0.3);
            margin-bottom: 30px;
        }}
        
        .insight {{
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .insight:last-child {{
            border-bottom: none;
        }}
        
        .insight-icon {{
            display: inline-block;
            width: 24px;
            text-align: center;
            margin-right: 10px;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #8892b0;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            h1 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Dashboard Corrélation Sentiment-Crypto</h1>
            <p class="subtitle">Analyse de la relation entre le sentiment social et les prix BTC/ETH</p>
            <p class="subtitle">Période: {df['date'].min().strftime('%Y-%m-%d')} → {df['date'].max().strftime('%Y-%m-%d')} ({len(df)} jours)</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card btc">
                <div class="stat-label">Corrélation BTC</div>
                <div class="stat-value {'positive' if corr_btc > 0 else 'negative'}">{corr_btc:.4f}</div>
                <div class="stat-detail">Sentiment ↔ Retour journalier BTC</div>
            </div>
            
            <div class="stat-card eth">
                <div class="stat-label">Corrélation ETH</div>
                <div class="stat-value {'positive' if corr_eth > 0 else 'negative'}">{corr_eth:.4f}</div>
                <div class="stat-detail">Sentiment ↔ Retour journalier ETH</div>
            </div>
            
            <div class="stat-card sentiment">
                <div class="stat-label">Score Sentiment Moyen</div>
                <div class="stat-value {'positive' if df['score_mean'].mean() > 0 else 'negative'}">{df['score_mean'].mean():.4f}</div>
                <div class="stat-detail">Légèrement positif</div>
            </div>
            
            <div class="stat-card correlation">
                <div class="stat-label">Posts Analysés</div>
                <div class="stat-value neutral">{df['post_count'].sum():,}</div>
                <div class="stat-detail">Moyenne: {df['post_count'].mean():.0f} posts/jour</div>
            </div>
        </div>
        
        <div class="insights-section">
            <h2 class="section-title">🔍 Insights Clés</h2>
            <div class="insight">
                <span class="insight-icon">📈</span>
                <strong>Probabilité hausse BTC</strong> quand sentiment positif: <span style="color: #00C853;">{prob_btc_up_sent_pos:.1f}%</span>
            </div>
            <div class="insight">
                <span class="insight-icon">📈</span>
                <strong>Probabilité hausse ETH</strong> quand sentiment positif: <span style="color: #00C853;">{prob_eth_up_sent_pos:.1f}%</span>
            </div>
            <div class="insight">
                <span class="insight-icon">📊</span>
                La corrélation ETH ({corr_eth:.3f}) est {'plus forte' if abs(corr_eth) > abs(corr_btc) else 'plus faible'} que celle du BTC ({corr_btc:.3f})
            </div>
            <div class="insight">
                <span class="insight-icon">⚠️</span>
                Les corrélations restent <strong>faibles</strong> (< 0.3), indiquant que le sentiment seul n'est pas un prédicteur fiable des prix
            </div>
        </div>
        
        <div class="charts-section">
            <h2 class="section-title">📉 Visualisations</h2>
            
            <div class="charts-grid">
                <div class="chart-card">
                    <h3 class="chart-title">Matrice de Corrélation</h3>
                    <img src="plots/correlation_heatmap.png" alt="Heatmap de corrélation">
                </div>
                
                <div class="chart-card">
                    <h3 class="chart-title">Séries Temporelles</h3>
                    <img src="plots/time_series.png" alt="Séries temporelles">
                </div>
                
                <div class="chart-card">
                    <h3 class="chart-title">Scatter Plots</h3>
                    <img src="plots/scatter_correlations.png" alt="Scatter plots">
                </div>
                
                <div class="chart-card">
                    <h3 class="chart-title">Distribution du Sentiment</h3>
                    <img src="plots/sentiment_distribution.png" alt="Distribution sentiment">
                </div>
                
                <div class="chart-card">
                    <h3 class="chart-title">Analyse des Lags (Décalage Temporel)</h3>
                    <img src="plots/lag_analysis.png" alt="Analyse lag">
                </div>
            </div>
        </div>
        
        <footer>
            <p>Dashboard généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Crypto Analysis Project - Sentiment vs Price Correlation</p>
        </footer>
    </div>
</body>
</html>
"""
    
    dashboard_path = OUTPUT_DIR / "dashboard.html"
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"✓ Dashboard HTML sauvegardé: {dashboard_path}")
    return dashboard_path


def main():
    """Fonction principale"""
    logger.info("=" * 70)
    logger.info("GÉNÉRATION DU DASHBOARD DE CORRÉLATION")
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # Charger les données
    df = load_data()
    
    # Générer tous les graphiques
    logger.info("")
    logger.info("=" * 70)
    logger.info("GÉNÉRATION DES GRAPHIQUES")
    logger.info("=" * 70)
    
    plot_correlation_heatmap(df)
    plot_time_series(df)
    plot_scatter_correlations(df)
    plot_sentiment_distribution(df)
    plot_lag_analysis(df)
    
    # Générer le dashboard HTML
    logger.info("")
    logger.info("=" * 70)
    logger.info("GÉNÉRATION DU DASHBOARD HTML")
    logger.info("=" * 70)
    
    dashboard_path = generate_html_dashboard(df)
    
    # Résumé
    logger.info("")
    logger.info("=" * 70)
    logger.info("RÉSUMÉ")
    logger.info("=" * 70)
    logger.info(f"✓ 5 graphiques générés dans: {PLOTS_DIR}")
    logger.info(f"✓ Dashboard HTML: {dashboard_path}")
    logger.info("")
    logger.info("Pour voir le dashboard, ouvrez le fichier HTML dans votre navigateur.")
    logger.info("")
    logger.info("Génération terminée avec succès ✓")


if __name__ == "__main__":
    main()



