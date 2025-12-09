"""
Script pour aligner temporellement deux datasets de tweets/sentiment Bitcoin.

Ce script :
1. Lit deux fichiers CSV de tweets/sentiment
2. Trouve la période temporelle commune (intersection des dates)
3. Filtre chaque dataset pour ne garder que cette période commune
4. Sauvegarde deux nouveaux CSV filtrés dans un dossier de sortie

⚠️ Important :
- Chaque dataset reste séparé (pas de merge, pas de jointure)
- On filtre uniquement sur la date
- On ne fait aucune corrélation, aucun calcul de prix
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional


def identifier_colonne_date(df: pd.DataFrame, noms_possibles: list) -> Optional[str]:
    """
    Identifie la colonne de date dans un DataFrame.
    
    Args:
        df: DataFrame à analyser
        noms_possibles: Liste des noms de colonnes possibles (ex: ['date', 'Date', 'created_at'])
    
    Returns:
        Nom de la colonne trouvée ou None
    """
    for nom in noms_possibles:
        if nom in df.columns:
            return nom
    return None


def parser_dates_dataset1(df: pd.DataFrame, colonne_date: str) -> pd.DataFrame:
    """
    Parse les dates du Dataset 1 (crypto_sent.csv).
    
    Args:
        df: DataFrame du dataset 1
        colonne_date: Nom de la colonne de date (ex: 'created_at')
    
    Returns:
        DataFrame avec colonnes 'date' (date seule) et colonne datetime originale
    """
    # Créer une copie pour ne pas modifier l'original
    df_work = df.copy()
    
    # Convertir en datetime
    df_work[f'{colonne_date}_dt'] = pd.to_datetime(df_work[colonne_date], errors='coerce')
    
    # Créer une colonne date (jour seulement)
    df_work['date'] = df_work[f'{colonne_date}_dt'].dt.date
    
    return df_work


def parser_dates_dataset2(df: pd.DataFrame, colonne_date: str) -> pd.DataFrame:
    """
    Parse les dates du Dataset 2 (peut avoir différents formats).
    
    Args:
        df: DataFrame du dataset 2
        colonne_date: Nom de la colonne de date (ex: 'date', 'Date')
    
    Returns:
        DataFrame avec colonnes 'date' (date seule) et colonne datetime originale
    """
    # Créer une copie pour ne pas modifier l'original
    df_work = df.copy()
    
    # Convertir en datetime (pandas gère automatiquement les formats Twitter)
    df_work[f'{colonne_date}_dt'] = pd.to_datetime(df_work[colonne_date], errors='coerce')
    
    # Créer une colonne date (jour seulement)
    df_work['date'] = df_work[f'{colonne_date}_dt'].dt.date
    
    return df_work


def calculer_periode_commune(date_min_1: datetime.date, date_max_1: datetime.date,
                            date_min_2: datetime.date, date_max_2: datetime.date) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
    """
    Calcule la période temporelle commune entre deux datasets.
    
    Args:
        date_min_1: Date minimale du dataset 1
        date_max_1: Date maximale du dataset 1
        date_min_2: Date minimale du dataset 2
        date_max_2: Date maximale du dataset 2
    
    Returns:
        Tuple (date_min_commune, date_max_commune) ou (None, None) si pas d'intersection
    """
    # Calculer l'intersection
    date_min_commune = max(date_min_1, date_min_2)
    date_max_commune = min(date_max_1, date_max_2)
    
    # Vérifier s'il y a une intersection valide
    if date_min_commune > date_max_commune:
        return None, None
    
    return date_min_commune, date_max_commune


def filtrer_dataset(df: pd.DataFrame, date_min: datetime.date, date_max: datetime.date) -> pd.DataFrame:
    """
    Filtre un dataset pour ne garder que les lignes dans la période spécifiée.
    
    Args:
        df: DataFrame à filtrer (doit avoir une colonne 'date')
        date_min: Date minimale (incluse)
        date_max: Date maximale (incluse)
    
    Returns:
        DataFrame filtré
    """
    # Filtrer sur la période
    mask = (df['date'] >= date_min) & (df['date'] <= date_max)
    df_filtered = df[mask].copy()
    
    return df_filtered


def sauvegarder_dataset_filtre(df: pd.DataFrame, output_path: Path, colonnes_a_exclure: list = None) -> None:
    """
    Sauvegarde un dataset filtré en CSV, en excluant les colonnes temporaires.
    
    Args:
        df: DataFrame à sauvegarder
        output_path: Chemin de sortie
        colonnes_a_exclure: Liste des colonnes à exclure (ex: ['date', 'created_at_dt'])
    """
    df_to_save = df.copy()
    
    # Exclure les colonnes temporaires si spécifiées
    if colonnes_a_exclure:
        colonnes_finales = [col for col in df_to_save.columns if col not in colonnes_a_exclure]
        df_to_save = df_to_save[colonnes_finales]
    
    # Sauvegarder
    df_to_save.to_csv(output_path, index=False, encoding='utf-8')


def aligner_datasets_temporels(
    path_dataset1: str,
    path_dataset2: str,
    output_dir: str,
    colonne_date1: str = "created_at",
    colonnes_date2_possibles: list = None,
    nom_output1: str = "crypto_sent_aligned.csv",
    nom_output2: str = "btc_tweets_sentiment_aligned.csv"
) -> None:
    """
    Fonction principale pour aligner temporellement deux datasets.
    
    Args:
        path_dataset1: Chemin vers le premier CSV
        path_dataset2: Chemin vers le deuxième CSV
        output_dir: Dossier de sortie pour les CSV filtrés
        colonne_date1: Nom de la colonne de date dans le dataset 1
        colonnes_date2_possibles: Liste des noms possibles pour la colonne de date dans le dataset 2
        nom_output1: Nom du fichier de sortie pour le dataset 1 filtré
        nom_output2: Nom du fichier de sortie pour le dataset 2 filtré
    """
    if colonnes_date2_possibles is None:
        colonnes_date2_possibles = ['date', 'Date', 'created_at']
    
    print("="*80)
    print("ALIGNEMENT TEMPOREL DE DEUX DATASETS")
    print("="*80)
    print()
    
    # Créer le dossier de sortie
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # ============================================
    # 1. CHARGER LES DEUX DATASETS
    # ============================================
    print("1. Chargement des datasets...")
    print(f"   Dataset 1: {path_dataset1}")
    df1 = pd.read_csv(path_dataset1, low_memory=False)
    print(f"   ✓ Dataset 1 chargé: {len(df1):,} lignes, {len(df1.columns)} colonnes")
    
    print(f"   Dataset 2: {path_dataset2}")
    df2 = pd.read_csv(path_dataset2, low_memory=False)
    print(f"   ✓ Dataset 2 chargé: {len(df2):,} lignes, {len(df2.columns)} colonnes")
    print()
    
    # ============================================
    # 2. IDENTIFIER ET PARSER LES DATES
    # ============================================
    print("2. Parsing des dates...")
    
    # Dataset 1
    if colonne_date1 not in df1.columns:
        raise ValueError(f"Colonne '{colonne_date1}' non trouvée dans le dataset 1. Colonnes disponibles: {list(df1.columns)}")
    
    df1_parsed = parser_dates_dataset1(df1, colonne_date1)
    date_min_1 = df1_parsed['date'].min()
    date_max_1 = df1_parsed['date'].max()
    print(f"   Dataset 1 - Période originale: {date_min_1} → {date_max_1}")
    print(f"   Dataset 1 - Dates valides: {df1_parsed['date'].notna().sum():,} / {len(df1_parsed):,}")
    
    # Dataset 2
    colonne_date2 = identifier_colonne_date(df2, colonnes_date2_possibles)
    if colonne_date2 is None:
        raise ValueError(f"Aucune colonne de date trouvée dans le dataset 2. Colonnes disponibles: {list(df2.columns)}")
    
    print(f"   Colonne de date identifiée dans le dataset 2: '{colonne_date2}'")
    df2_parsed = parser_dates_dataset2(df2, colonne_date2)
    date_min_2 = df2_parsed['date'].min()
    date_max_2 = df2_parsed['date'].max()
    print(f"   Dataset 2 - Période originale: {date_min_2} → {date_max_2}")
    print(f"   Dataset 2 - Dates valides: {df2_parsed['date'].notna().sum():,} / {len(df2_parsed):,}")
    
    # Afficher la distribution des dates pour diagnostic
    dates_uniques = df2_parsed['date'].value_counts().sort_index()
    print(f"   Dataset 2 - Nombre de dates uniques: {len(dates_uniques)}")
    if len(dates_uniques) <= 10:
        print(f"   Dataset 2 - Dates présentes: {', '.join([str(d) for d in dates_uniques.index[:10]])}")
    else:
        print(f"   Dataset 2 - Premières dates: {', '.join([str(d) for d in dates_uniques.index[:5]])}")
        print(f"   Dataset 2 - Dernières dates: {', '.join([str(d) for d in dates_uniques.index[-5:]])}")
    print()
    
    # ============================================
    # 3. CALCULER LA PÉRIODE COMMUNE
    # ============================================
    print("3. Calcul de la période commune...")
    date_min_commune, date_max_commune = calculer_periode_commune(
        date_min_1, date_max_1, date_min_2, date_max_2
    )
    
    if date_min_commune is None or date_max_commune is None:
        print("   ⚠️ ERREUR: Aucune période commune trouvée entre les deux datasets!")
        print()
        print("   Détails des périodes:")
        print(f"   - Dataset 1: {date_min_1} → {date_max_1} ({(date_max_1 - date_min_1).days + 1} jours)")
        print(f"   - Dataset 2: {date_min_2} → {date_max_2} ({(date_max_2 - date_min_2).days + 1} jours)")
        print()
        
        # Calculer le gap
        if date_max_1 < date_min_2:
            gap = (date_min_2 - date_max_1).days
            print(f"   ⚠️ Gap détecté: {gap} jours entre la fin du dataset 1 ({date_max_1})")
            print(f"      et le début du dataset 2 ({date_min_2})")
        elif date_max_2 < date_min_1:
            gap = (date_min_1 - date_max_2).days
            print(f"   ⚠️ Gap détecté: {gap} jours entre la fin du dataset 2 ({date_max_2})")
            print(f"      et le début du dataset 1 ({date_min_1})")
        
        print()
        print("   Les datasets ne se chevauchent pas temporellement.")
        print("   Aucun fichier filtré ne sera créé.")
        print()
        print("   Suggestions:")
        print("   1. Vérifier si un autre fichier de dataset 2 est disponible")
        print("   2. Vérifier les dates dans les fichiers source")
        print("   3. Utiliser des datasets avec des périodes qui se chevauchent")
        return
    
    print(f"   ✓ Période commune: {date_min_commune} → {date_max_commune}")
    print(f"   Durée: {(date_max_commune - date_min_commune).days + 1} jours")
    print()
    
    # ============================================
    # 4. FILTRER LES DEUX DATASETS
    # ============================================
    print("4. Filtrage des datasets...")
    
    # Filtrer Dataset 1
    n_original_1 = len(df1_parsed)
    df1_filtered = filtrer_dataset(df1_parsed, date_min_commune, date_max_commune)
    n_filtered_1 = len(df1_filtered)
    print(f"   Dataset 1: {n_original_1:,} → {n_filtered_1:,} lignes ({n_filtered_1/n_original_1*100:.2f}% conservées)")
    
    # Filtrer Dataset 2
    n_original_2 = len(df2_parsed)
    df2_filtered = filtrer_dataset(df2_parsed, date_min_commune, date_max_commune)
    n_filtered_2 = len(df2_filtered)
    print(f"   Dataset 2: {n_original_2:,} → {n_filtered_2:,} lignes ({n_filtered_2/n_original_2*100:.2f}% conservées)")
    print()
    
    # ============================================
    # 5. SAUVEGARDER LES DATASETS FILTRÉS
    # ============================================
    print("5. Sauvegarde des datasets filtrés...")
    
    # Colonnes temporaires à exclure lors de la sauvegarde
    colonnes_temp_1 = ['date', f'{colonne_date1}_dt']
    colonnes_temp_2 = ['date', f'{colonne_date2}_dt']
    
    # Sauvegarder Dataset 1
    output_path_1 = output_path / nom_output1
    sauvegarder_dataset_filtre(df1_filtered, output_path_1, colonnes_temp_1)
    print(f"   ✓ Dataset 1 sauvegardé: {output_path_1}")
    
    # Sauvegarder Dataset 2
    output_path_2 = output_path / nom_output2
    sauvegarder_dataset_filtre(df2_filtered, output_path_2, colonnes_temp_2)
    print(f"   ✓ Dataset 2 sauvegardé: {output_path_2}")
    print()
    
    # ============================================
    # 6. RÉSUMÉ FINAL
    # ============================================
    print("="*80)
    print("RÉSUMÉ")
    print("="*80)
    print()
    print("Dataset 1:")
    print(f"  - Période originale: {date_min_1} → {date_max_1}")
    print(f"  - Période après filtrage: {date_min_commune} → {date_max_commune}")
    print(f"  - Lignes: {n_original_1:,} → {n_filtered_1:,}")
    print(f"  - Fichier de sortie: {output_path_1}")
    print()
    print("Dataset 2:")
    print(f"  - Période originale: {date_min_2} → {date_max_2}")
    print(f"  - Période après filtrage: {date_min_commune} → {date_max_commune}")
    print(f"  - Lignes: {n_original_2:,} → {n_filtered_2:,}")
    print(f"  - Fichier de sortie: {output_path_2}")
    print()
    print("="*80)
    print("✓ Alignement temporel terminé avec succès!")
    print("="*80)


def main():
    """
    Fonction principale avec les chemins spécifiques au projet.
    
    Aligne crypto_sent.csv avec les fichiers de prix générés par fetch_crypto_data_yfinance.py.
    """
    import sys
    
    # Chemins des datasets
    path_dataset1 = r"data/crypto_sent.csv"
    
    # Dataset 2: Fichiers de prix générés par fetch_crypto_data_yfinance.py
    # Par défaut: BTC, mais peut être changé via argument
    crypto_symbol = "BTC"  # Par défaut: BTC (peut être ETH ou SOL)
    
    if len(sys.argv) > 1:
        # Permettre de spécifier le symbole crypto (BTC, ETH, SOL)
        crypto_symbol = sys.argv[1].upper()
        if crypto_symbol not in ['BTC', 'ETH', 'SOL']:
            print(f"⚠️  Symbole crypto '{crypto_symbol}' non reconnu. Utilisation de BTC par défaut.")
            crypto_symbol = "BTC"
        print(f"Utilisation du dataset de prix: {crypto_symbol}")
    else:
        print("Utilisation du dataset de prix BTC par défaut.")
        print("Pour utiliser ETH ou SOL: python aligner_datasets_temporels.py ETH")
        print()
    
    # Chemin vers le fichier de prix
    path_dataset2 = f"data/bronze/{crypto_symbol}/historical_prices.csv"
    
    # Vérifier que le fichier existe
    if not Path(path_dataset2).exists():
        print(f"❌ ERREUR: Le fichier {path_dataset2} n'existe pas!")
        print(f"   Veuillez d'abord exécuter fetch_crypto_data/fetch_crypto_data_yfinance.py")
        print(f"   pour générer les fichiers de prix.")
        sys.exit(1)
    
    # Dossier de sortie
    output_dir = r"data/gold/aligned_datasets"
    
    # Noms des fichiers de sortie
    nom_output1 = "crypto_sent_aligned.csv"
    nom_output2 = f"{crypto_symbol.lower()}_prices_aligned.csv"
    
    # Paramètres de colonnes de date
    colonne_date1 = "created_at"
    colonnes_date2_possibles = ['date']  # Les fichiers de prix utilisent 'date'
    
    # Exécuter l'alignement
    try:
        aligner_datasets_temporels(
            path_dataset1=path_dataset1,
            path_dataset2=path_dataset2,
            output_dir=output_dir,
            colonne_date1=colonne_date1,
            colonnes_date2_possibles=colonnes_date2_possibles,
            nom_output1=nom_output1,
            nom_output2=nom_output2
        )
    except ValueError as e:
        print(f"\n❌ ERREUR: {e}")
        print("\n💡 Suggestions:")
        print("   1. Vérifiez que les deux datasets ont des périodes qui se chevauchent")
        print("   2. Vérifiez que les colonnes de date existent dans les deux datasets")
        print("   3. Essayez un autre dataset avec: python aligner_datasets_temporels.py <chemin_dataset2>")
        sys.exit(1)


if __name__ == "__main__":
    main()

