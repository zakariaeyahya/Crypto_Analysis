"""
Script d'analyse initiale du dataset crypto_sent.csv

Ce script effectue une analyse exploratoire complète du dataset de sentiment crypto:
- Structure et métadonnées
- Statistiques descriptives
- Distribution des sentiments
- Analyse temporelle
- Détection de valeurs manquantes et anomalies
- Visualisations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration des graphiques
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def charger_dataset(file_path: str) -> pd.DataFrame:
    """
    Charge le dataset depuis le fichier CSV.
    
    Args:
        file_path: Chemin vers le fichier CSV
    
    Returns:
        DataFrame avec les données
    """
    print(f"Chargement du dataset depuis: {file_path}")
    df = pd.read_csv(file_path, low_memory=False)
    print(f"✓ Dataset chargé: {len(df)} lignes, {len(df.columns)} colonnes\n")
    return df


def analyser_structure(df: pd.DataFrame) -> None:
    """
    Analyse la structure de base du dataset.
    """
    print("="*80)
    print("1. STRUCTURE DU DATASET")
    print("="*80)
    
    print(f"\nDimensions:")
    print(f"  - Nombre de lignes: {len(df):,}")
    print(f"  - Nombre de colonnes: {len(df.columns)}")
    print(f"  - Taille mémoire: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print(f"\nColonnes:")
    for i, col in enumerate(df.columns, 1):
        dtype = df[col].dtype
        print(f"  {i}. {col} ({dtype})")
    
    print(f"\nAperçu des premières lignes:")
    print(df.head(10).to_string())
    
    print(f"\nInformations générales:")
    print(df.info())


def analyser_valeurs_manquantes(df: pd.DataFrame) -> None:
    """
    Analyse les valeurs manquantes dans le dataset.
    """
    print("\n" + "="*80)
    print("2. VALEURS MANQUANTES")
    print("="*80)
    
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    
    missing_df = pd.DataFrame({
        'Colonne': missing.index,
        'Valeurs manquantes': missing.values,
        'Pourcentage': missing_pct.values
    })
    missing_df = missing_df[missing_df['Valeurs manquantes'] > 0].sort_values('Valeurs manquantes', ascending=False)
    
    if len(missing_df) > 0:
        print("\nColonnes avec valeurs manquantes:")
        print(missing_df.to_string(index=False))
    else:
        print("\n✓ Aucune valeur manquante détectée!")
    
    # Vérifier les valeurs vides dans les colonnes textuelles
    print("\nVérification des chaînes vides:")
    for col in df.select_dtypes(include=['object']).columns:
        empty_count = (df[col].astype(str).str.strip() == '').sum()
        if empty_count > 0:
            print(f"  - {col}: {empty_count} valeurs vides ({empty_count/len(df)*100:.2f}%)")


def analyser_doublons(df: pd.DataFrame) -> None:
    """
    Analyse les doublons dans le dataset.
    """
    print("\n" + "="*80)
    print("3. DOUBLONS")
    print("="*80)
    
    # Doublons complets
    duplicates_all = df.duplicated().sum()
    print(f"\nLignes complètement dupliquées: {duplicates_all:,} ({duplicates_all/len(df)*100:.2f}%)")
    
    # Doublons par ID
    if 'id' in df.columns:
        duplicates_id = df['id'].duplicated().sum()
        print(f"IDs dupliqués: {duplicates_id:,} ({duplicates_id/len(df)*100:.2f}%)")
    
    # Doublons par texte
    if 'text' in df.columns:
        duplicates_text = df['text'].duplicated().sum()
        print(f"Textes dupliqués: {duplicates_text:,} ({duplicates_text/len(df)*100:.2f}%)")


def analyser_sentiment(df: pd.DataFrame) -> None:
    """
    Analyse la distribution des sentiments.
    """
    print("\n" + "="*80)
    print("4. ANALYSE DES SENTIMENTS")
    print("="*80)
    
    if 'sentiment' not in df.columns:
        print("⚠ Colonne 'sentiment' non trouvée!")
        return
    
    print(f"\nDistribution des sentiments:")
    sentiment_counts = df['sentiment'].value_counts()
    sentiment_pct = df['sentiment'].value_counts(normalize=True) * 100
    
    sentiment_df = pd.DataFrame({
        'Sentiment': sentiment_counts.index,
        'Nombre': sentiment_counts.values,
        'Pourcentage': sentiment_pct.values
    })
    print(sentiment_df.to_string(index=False))
    
    # Visualisation
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    sentiment_counts.plot(kind='bar', color='steelblue')
    plt.title('Distribution des Sentiments (Comptage)', fontsize=14, fontweight='bold')
    plt.xlabel('Sentiment', fontsize=12)
    plt.ylabel('Nombre', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    plt.subplot(1, 2, 2)
    sentiment_pct.plot(kind='bar', color='coral')
    plt.title('Distribution des Sentiments (Pourcentage)', fontsize=14, fontweight='bold')
    plt.xlabel('Sentiment', fontsize=12)
    plt.ylabel('Pourcentage (%)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/analyse_sentiment_distribution.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Graphique sauvegardé: data/analyse_sentiment_distribution.png")
    plt.close()


def analyser_scores(df: pd.DataFrame) -> None:
    """
    Analyse les scores de sentiment.
    """
    print("\n" + "="*80)
    print("5. ANALYSE DES SCORES")
    print("="*80)
    
    if 'score' not in df.columns:
        print("⚠ Colonne 'score' non trouvée!")
        return
    
    # Convertir en numérique si nécessaire
    df['score'] = pd.to_numeric(df['score'], errors='coerce')
    
    print(f"\nStatistiques descriptives des scores:")
    print(df['score'].describe().to_string())
    
    print(f"\nStatistiques détaillées:")
    print(f"  - Moyenne: {df['score'].mean():.4f}")
    print(f"  - Médiane: {df['score'].median():.4f}")
    print(f"  - Écart-type: {df['score'].std():.4f}")
    print(f"  - Minimum: {df['score'].min():.4f}")
    print(f"  - Maximum: {df['score'].max():.4f}")
    print(f"  - Q1 (25%): {df['score'].quantile(0.25):.4f}")
    print(f"  - Q3 (75%): {df['score'].quantile(0.75):.4f}")
    print(f"  - IQR: {df['score'].quantile(0.75) - df['score'].quantile(0.25):.4f}")
    
    # Valeurs aberrantes
    Q1 = df['score'].quantile(0.25)
    Q3 = df['score'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df['score'] < lower_bound) | (df['score'] > upper_bound)]
    print(f"\nValeurs aberrantes (méthode IQR): {len(outliers):,} ({len(outliers)/len(df)*100:.2f}%)")
    
    # Visualisation
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.hist(df['score'].dropna(), bins=50, color='steelblue', edgecolor='black', alpha=0.7)
    plt.title('Distribution des Scores', fontsize=14, fontweight='bold')
    plt.xlabel('Score', fontsize=12)
    plt.ylabel('Fréquence', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    plt.subplot(1, 3, 2)
    df['score'].plot(kind='box', vert=True)
    plt.title('Box Plot des Scores', fontsize=14, fontweight='bold')
    plt.ylabel('Score', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    plt.subplot(1, 3, 3)
    # Distribution par sentiment si disponible
    if 'sentiment' in df.columns:
        sentiments = df['sentiment'].unique()
        for sent in sentiments:
            scores = df[df['sentiment'] == sent]['score'].dropna()
            plt.hist(scores, bins=30, alpha=0.6, label=sent)
        plt.title('Distribution des Scores par Sentiment', fontsize=14, fontweight='bold')
        plt.xlabel('Score', fontsize=12)
        plt.ylabel('Fréquence', fontsize=12)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/analyse_scores_distribution.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Graphique sauvegardé: data/analyse_scores_distribution.png")
    plt.close()


def analyser_temporel(df: pd.DataFrame) -> None:
    """
    Analyse temporelle du dataset.
    """
    print("\n" + "="*80)
    print("6. ANALYSE TEMPORELLE")
    print("="*80)
    
    if 'created_at' not in df.columns:
        print("⚠ Colonne 'created_at' non trouvée!")
        return
    
    # Convertir en datetime
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    
    # Filtrer les dates valides
    df_valid_dates = df[df['created_at'].notna()]
    
    if len(df_valid_dates) == 0:
        print("⚠ Aucune date valide trouvée!")
        return
    
    print(f"\nPériode couverte:")
    print(f"  - Date minimale: {df_valid_dates['created_at'].min()}")
    print(f"  - Date maximale: {df_valid_dates['created_at'].max()}")
    print(f"  - Durée: {(df_valid_dates['created_at'].max() - df_valid_dates['created_at'].min()).days} jours")
    
    # Distribution par année
    df_valid_dates['year'] = df_valid_dates['created_at'].dt.year
    df_valid_dates['month'] = df_valid_dates['created_at'].dt.month
    df_valid_dates['day'] = df_valid_dates['created_at'].dt.day
    
    print(f"\nDistribution par année:")
    year_counts = df_valid_dates['year'].value_counts().sort_index()
    for year, count in year_counts.items():
        print(f"  - {year}: {count:,} enregistrements ({count/len(df_valid_dates)*100:.2f}%)")
    
    # Visualisation temporelle
    plt.figure(figsize=(15, 10))
    
    # Graphique 1: Volume par date
    plt.subplot(2, 2, 1)
    daily_counts = df_valid_dates.groupby(df_valid_dates['created_at'].dt.date).size()
    daily_counts.plot(kind='line', color='steelblue', linewidth=1.5)
    plt.title('Volume d\'enregistrements par jour', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Nombre d\'enregistrements', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(alpha=0.3)
    
    # Graphique 2: Distribution par année
    plt.subplot(2, 2, 2)
    year_counts.plot(kind='bar', color='coral')
    plt.title('Distribution par année', fontsize=14, fontweight='bold')
    plt.xlabel('Année', fontsize=12)
    plt.ylabel('Nombre d\'enregistrements', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', alpha=0.3)
    
    # Graphique 3: Distribution par mois (toutes années confondues)
    plt.subplot(2, 2, 3)
    month_counts = df_valid_dates['month'].value_counts().sort_index()
    month_counts.plot(kind='bar', color='lightgreen')
    plt.title('Distribution par mois', fontsize=14, fontweight='bold')
    plt.xlabel('Mois', fontsize=12)
    plt.ylabel('Nombre d\'enregistrements', fontsize=12)
    plt.xticks(range(12), ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                           'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'], rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Graphique 4: Évolution du sentiment moyen par mois
    if 'sentiment' in df_valid_dates.columns and 'score' in df_valid_dates.columns:
        plt.subplot(2, 2, 4)
        monthly_scores = df_valid_dates.groupby([df_valid_dates['created_at'].dt.to_period('M')])['score'].mean()
        monthly_scores.plot(kind='line', color='purple', linewidth=2, marker='o')
        plt.title('Score moyen de sentiment par mois', fontsize=14, fontweight='bold')
        plt.xlabel('Mois', fontsize=12)
        plt.ylabel('Score moyen', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/analyse_temporelle.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Graphique sauvegardé: data/analyse_temporelle.png")
    plt.close()


def analyser_textes(df: pd.DataFrame) -> None:
    """
    Analyse des textes (longueur, caractères spéciaux, etc.).
    """
    print("\n" + "="*80)
    print("7. ANALYSE DES TEXTES")
    print("="*80)
    
    if 'text' not in df.columns:
        print("⚠ Colonne 'text' non trouvée!")
        return
    
    # Convertir en string et nettoyer
    df['text'] = df['text'].astype(str)
    
    # Longueur des textes
    df['text_length'] = df['text'].str.len()
    df['word_count'] = df['text'].str.split().str.len()
    
    print(f"\nStatistiques de longueur des textes:")
    print(f"  - Longueur moyenne (caractères): {df['text_length'].mean():.1f}")
    print(f"  - Longueur médiane (caractères): {df['text_length'].median():.1f}")
    print(f"  - Longueur min (caractères): {df['text_length'].min()}")
    print(f"  - Longueur max (caractères): {df['text_length'].max()}")
    
    print(f"\nStatistiques du nombre de mots:")
    print(f"  - Nombre moyen de mots: {df['word_count'].mean():.1f}")
    print(f"  - Nombre médian de mots: {df['word_count'].median():.1f}")
    print(f"  - Nombre min de mots: {df['word_count'].min()}")
    print(f"  - Nombre max de mots: {df['word_count'].max()}")
    
    # Visualisation
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.hist(df['text_length'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
    plt.title('Distribution de la longueur des textes', fontsize=14, fontweight='bold')
    plt.xlabel('Longueur (caractères)', fontsize=12)
    plt.ylabel('Fréquence', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    plt.subplot(1, 3, 2)
    plt.hist(df['word_count'], bins=50, color='coral', edgecolor='black', alpha=0.7)
    plt.title('Distribution du nombre de mots', fontsize=14, fontweight='bold')
    plt.xlabel('Nombre de mots', fontsize=12)
    plt.ylabel('Fréquence', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    plt.subplot(1, 3, 3)
    # Longueur moyenne par sentiment
    if 'sentiment' in df.columns:
        sentiment_lengths = df.groupby('sentiment')['text_length'].mean().sort_values(ascending=False)
        sentiment_lengths.plot(kind='bar', color='lightgreen')
        plt.title('Longueur moyenne par sentiment', fontsize=14, fontweight='bold')
        plt.xlabel('Sentiment', fontsize=12)
        plt.ylabel('Longueur moyenne (caractères)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/analyse_textes.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Graphique sauvegardé: data/analyse_textes.png")
    plt.close()


def generer_rapport_complet(df: pd.DataFrame, output_file: str = "data/rapport_analyse_initial.txt") -> None:
    """
    Génère un rapport texte complet de l'analyse.
    """
    print("\n" + "="*80)
    print("8. GÉNÉRATION DU RAPPORT")
    print("="*80)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RAPPORT D'ANALYSE INITIALE - DATASET CRYPTO_SENT.CSV\n")
        f.write("="*80 + "\n")
        f.write(f"Date de génération: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("1. RÉSUMÉ GÉNÉRAL\n")
        f.write("-"*80 + "\n")
        f.write(f"Nombre total d'enregistrements: {len(df):,}\n")
        f.write(f"Nombre de colonnes: {len(df.columns)}\n")
        f.write(f"Colonnes: {', '.join(df.columns.tolist())}\n\n")
        
        f.write("2. VALEURS MANQUANTES\n")
        f.write("-"*80 + "\n")
        missing = df.isnull().sum()
        for col in df.columns:
            f.write(f"{col}: {missing[col]:,} ({missing[col]/len(df)*100:.2f}%)\n")
        f.write("\n")
        
        if 'sentiment' in df.columns:
            f.write("3. DISTRIBUTION DES SENTIMENTS\n")
            f.write("-"*80 + "\n")
            sentiment_counts = df['sentiment'].value_counts()
            for sent, count in sentiment_counts.items():
                f.write(f"{sent}: {count:,} ({count/len(df)*100:.2f}%)\n")
            f.write("\n")
        
        if 'score' in df.columns:
            f.write("4. STATISTIQUES DES SCORES\n")
            f.write("-"*80 + "\n")
            df['score'] = pd.to_numeric(df['score'], errors='coerce')
            f.write(f"Moyenne: {df['score'].mean():.4f}\n")
            f.write(f"Médiane: {df['score'].median():.4f}\n")
            f.write(f"Écart-type: {df['score'].std():.4f}\n")
            f.write(f"Min: {df['score'].min():.4f}\n")
            f.write(f"Max: {df['score'].max():.4f}\n\n")
        
        if 'created_at' in df.columns:
            f.write("5. PÉRIODE TEMPORELLE\n")
            f.write("-"*80 + "\n")
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            df_valid = df[df['created_at'].notna()]
            if len(df_valid) > 0:
                f.write(f"Date minimale: {df_valid['created_at'].min()}\n")
                f.write(f"Date maximale: {df_valid['created_at'].max()}\n")
                f.write(f"Durée: {(df_valid['created_at'].max() - df_valid['created_at'].min()).days} jours\n\n")
        
        if 'text' in df.columns:
            f.write("6. STATISTIQUES DES TEXTES\n")
            f.write("-"*80 + "\n")
            df['text'] = df['text'].astype(str)
            df['text_length'] = df['text'].str.len()
            f.write(f"Longueur moyenne: {df['text_length'].mean():.1f} caractères\n")
            f.write(f"Longueur médiane: {df['text_length'].median():.1f} caractères\n")
            f.write(f"Longueur min: {df['text_length'].min()} caractères\n")
            f.write(f"Longueur max: {df['text_length'].max()} caractères\n")
    
    print(f"✓ Rapport sauvegardé: {output_file}")


def main():
    """
    Fonction principale qui orchestre toute l'analyse.
    """
    file_path = r"D:\bureau\BD_AI1\ci3\taln\Crypto\Crypto_Analysis\data\crypto_sent.csv"
    
    # Créer le dossier data s'il n'existe pas
    Path('data').mkdir(exist_ok=True)
    
    print("="*80)
    print("ANALYSE INITIALE DU DATASET CRYPTO_SENT.CSV")
    print("="*80)
    print()
    
    # Charger le dataset
    df = charger_dataset(file_path)
    
    # Effectuer toutes les analyses
    analyser_structure(df)
    analyser_valeurs_manquantes(df)
    analyser_doublons(df)
    analyser_sentiment(df)
    analyser_scores(df)
    analyser_temporel(df)
    analyser_textes(df)
    generer_rapport_complet(df)
    
    print("\n" + "="*80)
    print("ANALYSE TERMINÉE!")
    print("="*80)
    print("\nFichiers générés:")
    print("  - data/analyse_sentiment_distribution.png")
    print("  - data/analyse_scores_distribution.png")
    print("  - data/analyse_temporelle.png")
    print("  - data/analyse_textes.png")
    print("  - data/rapport_analyse_initial.txt")


if __name__ == "__main__":
    main()

