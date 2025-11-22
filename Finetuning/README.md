# Fine-tuning de RoBERTa pour l'Analyse de Sentiment des Tweets Crypto

Ce projet implémente le fine-tuning du modèle RoBERTa pour classifier le sentiment des tweets Bitcoin en utilisant un dataset de 19+ millions de tweets.

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Résultats](#résultats)
- [Documentation](#documentation)

## 🎯 Vue d'ensemble

Le projet fine-tune le modèle **RoBERTa** (spécifiquement `cardiffnlp/twitter-roberta-base-sentiment`) pour classifier le sentiment des tweets crypto en trois catégories :
- **POSITIF** : Sentiment positif
- **NEGATIF** : Sentiment négatif  
- **NEUTRE** : Sentiment neutre

### Caractéristiques principales

- ✅ Support CUDA/GPU pour l'entraînement accéléré
- ✅ Mixed precision training (FP16) pour optimiser la mémoire
- ✅ Gestion de datasets volumineux (chargement par chunks)
- ✅ Early stopping pour éviter l'overfitting
- ✅ Checkpoints automatiques
- ✅ Visualisations complètes des résultats
- ✅ Script d'inférence pour nouvelles prédictions

### 📓 Format du code

Ce projet est disponible sous **deux formats équivalents** :

1. **Fichiers Python (.py)** : Code modulaire organisé en scripts séparés
   - `data_preparation.py`, `preprocessing.py`, `train.py`, `evaluate.py`, etc.
   - Idéal pour l'exécution en ligne de commande et l'intégration dans des pipelines

2. **Notebook Jupyter (.ipynb)** : `roberta-1-1.ipynb`
   - Contient **exactement le même code** que les fichiers .py
   - Organisé en cellules pour une exploration interactive
   - Idéal pour le développement, le débogage et la visualisation étape par étape

**Note importante** : Le notebook `roberta-1-1.ipynb` et les fichiers `.py` implémentent la même logique et produisent les mêmes résultats. Les résultats d'entraînement générés par le notebook sont disponibles dans le dossier `output/`. Pour une interprétation détaillée des résultats, consultez `output/results/README_INTERPRETATION.md`.

## 📁 Structure du projet

```
Finetuning/
├── config.yaml              # Configuration globale
├── data_preparation.py      # Chargement et analyse des données
├── preprocessing.py         # Nettoyage et préprocessing des textes
├── model_config.py          # Configuration du modèle RoBERTa
├── train.py                 # Script d'entraînement principal
├── evaluate.py              # Évaluation du modèle
├── inference.py             # Prédictions sur nouveaux tweets
├── visualize.py             # Visualisations des résultats
├── utils.py                 # Fonctions utilitaires
├── requirements.txt         # Dépendances Python
├── README.md                # Documentation
├── roberta-1-1.ipynb        # Notebook Jupyter (même code que les .py)
├── roberta_finetuning_prompt.txt  # Prompt original du projet
├── models/                  # Modèles sauvegardés
├── logs/                    # Logs d'entraînement
├── checkpoints/             # Checkpoints intermédiaires
├── results/                 # Résultats et visualisations
└── output/                  # Résultats générés par le notebook
    ├── models/              # Modèles entraînés
    │   ├── best_model/      # Meilleur modèle
    │   ├── final_model/     # Modèle final
    │   └── label_mapping.json
    └── results/              # Métriques et visualisations
        ├── training_metrics.json
        ├── training_curves.png
        ├── confusion_matrix.png
        ├── train_split.csv
        ├── val_split.csv
        ├── test_split.csv
        └── README_INTERPRETATION.md  # Interprétation détaillée des résultats
```

## 🚀 Installation

### Prérequis

- Python 3.8+
- CUDA-capable GPU (recommandé, 8GB+ VRAM)
- 10GB+ d'espace disque pour le dataset

### Installation des dépendances

```bash
pip install -r Finetuning/requirements.txt
```

### Installation de PyTorch avec CUDA

Pour utiliser le GPU, installez PyTorch avec support CUDA :

```bash
# Pour CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Pour CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Vérifiez que CUDA est disponible :

```python
import torch
print(torch.cuda.is_available())  # Doit retourner True
print(torch.cuda.get_device_name(0))  # Nom du GPU
```

## ⚙️ Configuration

Le fichier `config.yaml` contient toute la configuration du projet. Principales sections :

### Modèle
- `model.name` : Modèle Hugging Face à utiliser
- `model.num_labels` : Nombre de classes (3 pour sentiment)
- `model.max_length` : Longueur maximale des séquences (128 tokens)

### Données
- `data.csv_path` : Chemin vers le dataset CSV
- `data.sample_size` : Nombre de tweets à utiliser (None = tout)
- `data.train_split`, `data.val_split`, `data.test_split` : Proportions des splits

### Entraînement
- `training.batch_size` : Taille des batches (32 par défaut)
- `training.learning_rate` : Taux d'apprentissage (2e-5 par défaut)
- `training.num_epochs` : Nombre d'epochs (5 par défaut)
- `training.use_fp16` : Mixed precision training (True par défaut)
- `training.use_cuda` : Utiliser CUDA si disponible (True par défaut)

## 📖 Utilisation

### 1. Préparation des données

Le dataset doit être dans `data/bronze/kaggle/bitcoin_tweets_YYYYMMDD_HHMMSS.csv` avec les colonnes :
- `Date` : Date du tweet
- `text` : Texte du tweet
- `Sentiment` : Label (POSITIF/NEGATIF/NEUTRE)

### 2. Entraînement

Lancer l'entraînement :

```bash
python Finetuning/train.py
```

Le script va :
1. Charger et analyser les données
2. Préprocesser les textes
3. Diviser en train/val/test
4. Entraîner le modèle avec CUDA
5. Sauvegarder les checkpoints et le modèle final

### 3. Évaluation

Évaluer le modèle sur le test set :

```bash
python Finetuning/evaluate.py
```

Cela génère :
- Métriques détaillées (accuracy, F1, precision, recall)
- Matrice de confusion
- Classification report
- Fichier JSON avec tous les résultats

### 4. Visualisations

Créer les visualisations :

```bash
python Finetuning/visualize.py
```

Génère :
- Courbes d'entraînement (loss, accuracy, F1)
- Matrice de confusion
- Comparaison des métriques par classe

### 5. Inférence

Prédire le sentiment de nouveaux tweets :

```python
from Finetuning.inference import SentimentPredictor

# Charger le modèle
predictor = SentimentPredictor(
    model_path="Finetuning/models/roberta-bitcoin-sentiment",
    use_cuda=True
)

# Prédiction simple
sentiment = predictor.predict("Bitcoin is going to the moon! 🚀")
print(sentiment)  # "POSITIF"

# Prédiction avec probabilités
result = predictor.predict("Bitcoin is going to the moon! 🚀", return_proba=True)
print(result)
# {
#     "label": "POSITIF",
#     "probabilities": {"POSITIF": 0.85, "NEUTRE": 0.10, "NEGATIF": 0.05},
#     "confidence": 0.85
# }

# Prédiction par batch
tweets = ["Tweet 1", "Tweet 2", "Tweet 3"]
predictions = predictor.predict_batch(tweets, batch_size=32)
```

## 📊 Résultats

### Métriques cibles

- Accuracy > 75%
- F1-Score macro > 0.70
- F1-Score par classe > 0.65
- Temps d'inférence < 100ms par tweet

### Résultats d'entraînement

Les résultats de l'entraînement effectué via le notebook `roberta-1-1.ipynb` sont disponibles dans `Finetuning/output/` :

**Métriques obtenues** :
- **Accuracy (validation)** : 70.1%
- **F1-Score macro (validation)** : 0.686 (68.6%)
- **Meilleur F1-Score** : 0.686 (epoch 8)
- **Temps d'entraînement** : ~8.8 heures (8 epochs)

Pour une **interprétation détaillée** des résultats, consultez :
- 📄 `output/results/README_INTERPRETATION.md` : Analyse complète des performances, évolution des métriques, recommandations d'amélioration

### Fichiers générés

Après l'entraînement, vous trouverez dans `Finetuning/results/` (ou `Finetuning/output/results/` pour le notebook) :

- `training_metrics.json` : Métriques d'entraînement
- `evaluation_results.json` : Résultats d'évaluation
- `training_curves.png` : Courbes d'entraînement
- `confusion_matrix.png` : Matrice de confusion
- `metrics_comparison.png` : Comparaison des métriques

Dans `Finetuning/models/` (ou `Finetuning/output/models/` pour le notebook) :

- `best_model/` : Meilleur modèle basé sur validation F1-score
- `final_model/` : Modèle final après tous les epochs
- `label_mapping.json` : Mapping des labels

Dans `Finetuning/checkpoints/` :

- `checkpoint_epoch_N.pt` : Checkpoints par epoch
- `best_model.pt` : Meilleur modèle (basé sur F1 validation)

## 🔧 Optimisations

### Pour GPU avec mémoire limitée

1. Réduire `batch_size` (16 ou 8)
2. Activer `gradient_accumulation_steps` (2 ou 4)
3. Utiliser `use_fp16: true` pour mixed precision
4. Réduire `max_length` (64 ou 96 au lieu de 128)

### Pour datasets très volumineux

1. Utiliser `sample_size` pour échantillonner
2. Augmenter `chunk_size` pour le chargement
3. Utiliser data streaming (à implémenter)

## 🐛 Dépannage

### CUDA non disponible

Si `torch.cuda.is_available()` retourne `False` :

1. Vérifier l'installation de PyTorch avec CUDA
2. Vérifier que les drivers NVIDIA sont à jour
3. Le code basculera automatiquement sur CPU

### Erreur de mémoire GPU

1. Réduire `batch_size`
2. Activer `use_fp16: true`
3. Réduire `sample_size` pour utiliser moins de données

### Dataset trop volumineux

1. Utiliser `sample_size` dans la config (ex: 1000000)
2. Augmenter `chunk_size` pour le chargement

## 📚 Documentation

- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [RoBERTa Paper](https://arxiv.org/abs/1907.11692)
- [PyTorch Documentation](https://pytorch.org/docs/)

## 📝 Notes

- Le dataset complet fait ~3GB avec 19M tweets
- L'entraînement sur le dataset complet peut prendre plusieurs heures/jours
- Commencer avec un échantillon (100k-1M tweets) pour tester
- Le modèle utilise `cardiffnlp/twitter-roberta-base-sentiment` qui est pré-entraîné sur Twitter

## 🤝 Contribution

Pour améliorer le projet :
1. Tester différents hyperparamètres
2. Essayer d'autres modèles pré-entraînés
3. Implémenter data augmentation
4. Ajouter cross-validation

## 📄 Licence

Ce projet fait partie du projet Crypto_Analysis.





