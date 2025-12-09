"""
Script de diagnostic pour identifier les périodes temporelles des datasets disponibles.

Ce script analyse tous les fichiers CSV de tweets/sentiment pour trouver
les périodes couvertes et identifier les datasets qui pourraient se chevaucher.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def analyser_periode_dataset(file_path: str, colonnes_date_possibles: list = None) -> dict:
    """
    Analyse la période temporelle d'un dataset.
    
    Args:
        file_path: Chemin vers le fichier CSV
        colonnes_date_possibles: Liste des noms de colonnes de date possibles
    
    Returns:
        Dictionnaire avec les informations de période
    """
    if colonnes_date_possibles is None:
        colonnes_date_possibles = ['date', 'Date', 'created_at', 'created_utc']
    
    result = {
        'file_path': file_path,
        'success': False,
        'error': None,
        'date_min': None,
        'date_max': None,
        'nb_lignes': 0,
        'nb_dates_valides': 0,
        'nb_dates_uniques': 0,
        'colonne_date': None,
        'dates_uniques': []
    }
    
    try:
        # Lire un échantillon pour identifier la colonne de date
        df_sample = pd.read_csv(file_path, nrows=100, low_memory=False)
        
        # Identifier la colonne de date
        colonne_date = None
        for col in colonnes_date_possibles:
            if col in df_sample.columns:
                colonne_date = col
                break
        
        if colonne_date is None:
            result['error'] = f"Aucune colonne de date trouvée. Colonnes: {list(df_sample.columns)}"
            return result
        
        result['colonne_date'] = colonne_date
        
        # Lire le fichier complet (en chunks si trop gros)
        try:
            df = pd.read_csv(file_path, low_memory=False)
            result['nb_lignes'] = len(df)
            
            # Parser les dates
            df[f'{colonne_date}_dt'] = pd.to_datetime(df[colonne_date], errors='coerce')
            df['date'] = df[f'{colonne_date}_dt'].dt.date
            
            # Statistiques
            dates_valides = df['date'].notna()
            result['nb_dates_valides'] = dates_valides.sum()
            
            if result['nb_dates_valides'] > 0:
                dates_uniques = df[dates_valides]['date'].unique()
                result['nb_dates_uniques'] = len(dates_uniques)
                result['date_min'] = df[dates_valides]['date'].min()
                result['date_max'] = df[dates_valides]['date'].max()
                result['dates_uniques'] = sorted(dates_uniques)[:20]  # Premières 20 dates
                result['success'] = True
            else:
                result['error'] = "Aucune date valide trouvée"
        
        except MemoryError:
            # Si le fichier est trop gros, analyser par chunks
            result['error'] = "Fichier trop volumineux pour analyse complète"
            # Analyser un échantillon
            df_sample_full = pd.read_csv(file_path, nrows=10000, low_memory=False)
            result['nb_lignes'] = ">10000 (échantillon)"
            df_sample_full[f'{colonne_date}_dt'] = pd.to_datetime(df_sample_full[colonne_date], errors='coerce')
            df_sample_full['date'] = df_sample_full[f'{colonne_date}_dt'].dt.date
            dates_valides = df_sample_full['date'].notna()
            if dates_valides.sum() > 0:
                result['date_min'] = df_sample_full[dates_valides]['date'].min()
                result['date_max'] = df_sample_full[dates_valides]['date'].max()
                result['nb_dates_uniques'] = df_sample_full[dates_valides]['date'].nunique()
                result['success'] = True
    
    except Exception as e:
        result['error'] = str(e)
    
    return result


def trouver_chevauchements(results: list) -> list:
    """
    Trouve les paires de datasets qui se chevauchent temporellement.
    
    Args:
        results: Liste de résultats d'analyse
    
    Returns:
        Liste de tuples (dataset1, dataset2) qui se chevauchent
    """
    chevauchements = []
    
    for i, res1 in enumerate(results):
        if not res1['success']:
            continue
        
        for j, res2 in enumerate(results[i+1:], start=i+1):
            if not res2['success']:
                continue
            
            # Vérifier le chevauchement
            if res1['date_max'] >= res2['date_min'] and res1['date_min'] <= res2['date_max']:
                date_min_commune = max(res1['date_min'], res2['date_min'])
                date_max_commune = min(res1['date_max'], res2['date_max'])
                duree = (date_max_commune - date_min_commune).days + 1
                
                chevauchements.append({
                    'dataset1': res1['file_path'],
                    'dataset2': res2['file_path'],
                    'date_min_commune': date_min_commune,
                    'date_max_commune': date_max_commune,
                    'duree_jours': duree
                })
    
    return chevauchements


def main():
    """
    Fonction principale pour analyser tous les datasets disponibles.
    """
    print("="*80)
    print("DIAGNOSTIC DES PÉRIODES TEMPORELLES DES DATASETS")
    print("="*80)
    print()
    
    # Liste des fichiers à analyser
    fichiers_a_analyser = [
        "data/crypto_sent.csv",
        "data/bronze/kaggle/aisolutions353_btc-tweets-sentiment/BTC_Tweets_Updated.csv",
        "data/bronze/kaggle/kaushiksuresh147_bitcoin-tweets/Bitcoin_tweets_dataset_2.csv",
        "data/bronze/kaggle/bitcoin_tweets_20251119_165829.csv",
    ]
    
    print("Analyse des datasets...")
    print()
    
    results = []
    for fichier in fichiers_a_analyser:
        file_path = Path(fichier)
        if not file_path.exists():
            print(f"⚠ {fichier} - Fichier non trouvé")
            continue
        
        print(f"Analyse de: {fichier}")
        result = analyser_periode_dataset(str(file_path))
        results.append(result)
        
        if result['success']:
            print(f"  ✓ Période: {result['date_min']} → {result['date_max']}")
            print(f"    Lignes: {result['nb_lignes']:,}, Dates uniques: {result['nb_dates_uniques']}")
            print(f"    Colonne date: {result['colonne_date']}")
        else:
            print(f"  ✗ Erreur: {result['error']}")
        print()
    
    # Afficher le résumé
    print("="*80)
    print("RÉSUMÉ DES PÉRIODES")
    print("="*80)
    print()
    
    for result in results:
        if result['success']:
            print(f"{Path(result['file_path']).name}:")
            print(f"  Période: {result['date_min']} → {result['date_max']}")
            print(f"  Durée: {(result['date_max'] - result['date_min']).days + 1} jours")
            print(f"  Lignes: {result['nb_lignes']:,}")
            print(f"  Dates uniques: {result['nb_dates_uniques']}")
            print()
    
    # Trouver les chevauchements
    print("="*80)
    print("CHEVAUCHEMENTS TEMPORELS DÉTECTÉS")
    print("="*80)
    print()
    
    chevauchements = trouver_chevauchements(results)
    
    if chevauchements:
        for i, chev in enumerate(chevauchements, 1):
            print(f"{i}. Chevauchement trouvé:")
            print(f"   Dataset 1: {Path(chev['dataset1']).name}")
            print(f"   Dataset 2: {Path(chev['dataset2']).name}")
            print(f"   Période commune: {chev['date_min_commune']} → {chev['date_max_commune']}")
            print(f"   Durée: {chev['duree_jours']} jours")
            print()
    else:
        print("⚠ Aucun chevauchement temporel détecté entre les datasets analysés.")
        print()
        print("Les datasets ne se chevauchent pas. Vous devrez:")
        print("  1. Utiliser d'autres fichiers de datasets")
        print("  2. Ou accepter qu'il n'y ait pas de période commune")
        print()
    
    print("="*80)
    print("DIAGNOSTIC TERMINÉ")
    print("="*80)


if __name__ == "__main__":
    main()

