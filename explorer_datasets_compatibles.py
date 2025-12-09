"""
Script pour explorer tous les datasets disponibles et trouver ceux qui se chevauchent
avec crypto_sent.csv (2009-12-08 → 2018-02-19)
"""

import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def analyser_periode_dataset(file_path: str, colonnes_date_possibles: list = None) -> dict:
    """
    Analyse la période temporelle d'un dataset.
    
    Returns:
        dict avec les informations sur la période
    """
    if colonnes_date_possibles is None:
        colonnes_date_possibles = ['date', 'Date', 'created_at', 'timestamp']
    
    try:
        # Lire un échantillon pour identifier la colonne de date
        df_sample = pd.read_csv(file_path, nrows=1000, low_memory=False)
        
        # Identifier la colonne de date
        colonne_date = None
        for col in colonnes_date_possibles:
            if col in df_sample.columns:
                colonne_date = col
                break
        
        if colonne_date is None:
            return {
                'file': file_path,
                'status': 'no_date_column',
                'columns': list(df_sample.columns)
            }
        
        # Lire le dataset complet (ou un échantillon plus grand)
        print(f"  Analyse de {file_path}...")
        df = pd.read_csv(file_path, low_memory=False)
        
        # Parser les dates
        df[f'{colonne_date}_dt'] = pd.to_datetime(df[colonne_date], errors='coerce')
        df['date'] = df[f'{colonne_date}_dt'].dt.date
        
        # Filtrer les dates valides
        df_valid = df[df['date'].notna()]
        
        if len(df_valid) == 0:
            return {
                'file': file_path,
                'status': 'no_valid_dates',
                'colonne_date': colonne_date
            }
        
        date_min = df_valid['date'].min()
        date_max = df_valid['date'].max()
        n_dates_uniques = df_valid['date'].nunique()
        
        return {
            'file': file_path,
            'status': 'ok',
            'colonne_date': colonne_date,
            'date_min': date_min,
            'date_max': date_max,
            'n_dates_uniques': n_dates_uniques,
            'n_lignes': len(df),
            'n_lignes_valides': len(df_valid),
            'duree_jours': (date_max - date_min).days + 1
        }
        
    except Exception as e:
        return {
            'file': file_path,
            'status': 'error',
            'error': str(e)
        }


def verifier_chevauchement(periode1_min, periode1_max, periode2_min, periode2_max):
    """
    Vérifie si deux périodes se chevauchent.
    """
    date_min_commune = max(periode1_min, periode2_min)
    date_max_commune = min(periode1_max, periode2_max)
    
    if date_min_commune > date_max_commune:
        return False, None, None
    
    return True, date_min_commune, date_max_commune


def main():
    """
    Explore tous les datasets disponibles et trouve ceux compatibles avec crypto_sent.csv
    """
    print("="*80)
    print("EXPLORATION DES DATASETS COMPATIBLES")
    print("="*80)
    print()
    
    # Période de référence (crypto_sent.csv)
    print("1. Analyse du dataset de référence: crypto_sent.csv")
    ref_result = analyser_periode_dataset("data/crypto_sent.csv", ['created_at'])
    
    if ref_result['status'] != 'ok':
        print(f"   ❌ Erreur: {ref_result}")
        return
    
    ref_min = ref_result['date_min']
    ref_max = ref_result['date_max']
    
    print(f"   ✓ Période: {ref_min} → {ref_max}")
    print(f"   ✓ Durée: {ref_result['duree_jours']} jours")
    print(f"   ✓ Lignes: {ref_result['n_lignes']:,}")
    print()
    
    # Chercher tous les fichiers CSV dans le dossier data/bronze/kaggle
    print("2. Recherche des datasets dans data/bronze/kaggle/...")
    base_dir = Path("data/bronze/kaggle")
    
    fichiers_csv = []
    for pattern in ["**/*.csv"]:
        fichiers_csv.extend(base_dir.glob(pattern))
    
    print(f"   {len(fichiers_csv)} fichiers CSV trouvés")
    print()
    
    # Analyser chaque fichier
    print("3. Analyse des datasets...")
    print()
    
    resultats = []
    for fichier in fichiers_csv:
        resultat = analyser_periode_dataset(str(fichier))
        resultats.append(resultat)
    
    # Afficher les résultats
    print("="*80)
    print("RÉSULTATS")
    print("="*80)
    print()
    
    datasets_compatibles = []
    datasets_non_compatibles = []
    datasets_erreurs = []
    
    for resultat in resultats:
        if resultat['status'] == 'ok':
            chevauche, date_min_commune, date_max_commune = verifier_chevauchement(
                ref_min, ref_max, resultat['date_min'], resultat['date_max']
            )
            
            if chevauche:
                datasets_compatibles.append({
                    **resultat,
                    'date_min_commune': date_min_commune,
                    'date_max_commune': date_max_commune,
                    'duree_commune': (date_max_commune - date_min_commune).days + 1
                })
            else:
                datasets_non_compatibles.append(resultat)
        else:
            datasets_erreurs.append(resultat)
    
    # Afficher les datasets compatibles
    if datasets_compatibles:
        print("✅ DATASETS COMPATIBLES (avec chevauchement):")
        print("-"*80)
        for i, ds in enumerate(datasets_compatibles, 1):
            print(f"\n{i}. {Path(ds['file']).name}")
            print(f"   Chemin: {ds['file']}")
            print(f"   Colonne de date: {ds['colonne_date']}")
            print(f"   Période: {ds['date_min']} → {ds['date_max']} ({ds['duree_jours']} jours)")
            print(f"   Lignes: {ds['n_lignes']:,} ({ds['n_lignes_valides']:,} avec dates valides)")
            print(f"   Dates uniques: {ds['n_dates_uniques']}")
            print(f"   ✓ Période commune: {ds['date_min_commune']} → {ds['date_max_commune']} ({ds['duree_commune']} jours)")
    else:
        print("❌ AUCUN DATASET COMPATIBLE TROUVÉ")
        print()
    
    # Afficher les datasets non compatibles
    if datasets_non_compatibles:
        print("\n" + "="*80)
        print("⚠️  DATASETS NON COMPATIBLES (sans chevauchement):")
        print("-"*80)
        for i, ds in enumerate(datasets_non_compatibles, 1):
            gap = None
            if ds['date_min'] > ref_max:
                gap = (ds['date_min'] - ref_max).days
                gap_type = "après"
            elif ds['date_max'] < ref_min:
                gap = (ref_min - ds['date_max']).days
                gap_type = "avant"
            
            print(f"\n{i}. {Path(ds['file']).name}")
            print(f"   Chemin: {ds['file']}")
            print(f"   Période: {ds['date_min']} → {ds['date_max']} ({ds['duree_jours']} jours)")
            print(f"   Lignes: {ds['n_lignes']:,}")
            if gap is not None:
                print(f"   ⚠️  Gap de {gap} jours ({gap_type} la période de référence)")
    
    # Afficher les erreurs
    if datasets_erreurs:
        print("\n" + "="*80)
        print("❌ DATASETS AVEC ERREURS:")
        print("-"*80)
        for i, ds in enumerate(datasets_erreurs, 1):
            print(f"\n{i}. {Path(ds['file']).name}")
            print(f"   Statut: {ds['status']}")
            if 'error' in ds:
                print(f"   Erreur: {ds['error']}")
            if 'columns' in ds:
                print(f"   Colonnes disponibles: {', '.join(ds['columns'])}")
    
    # Résumé final
    print("\n" + "="*80)
    print("RÉSUMÉ")
    print("="*80)
    print(f"Datasets compatibles: {len(datasets_compatibles)}")
    print(f"Datasets non compatibles: {len(datasets_non_compatibles)}")
    print(f"Datasets avec erreurs: {len(datasets_erreurs)}")
    print()
    
    if datasets_compatibles:
        print("💡 Pour utiliser un dataset compatible, exécutez:")
        print(f"   python aligner_datasets_temporels.py \"{datasets_compatibles[0]['file']}\"")
    else:
        print("💡 Aucun dataset compatible trouvé. Options:")
        print("   1. Vérifier d'autres dossiers pour des datasets")
        print("   2. Utiliser un dataset externe avec une période qui chevauche")
        print("   3. Modifier les dates dans l'un des datasets existants")


if __name__ == "__main__":
    main()

