# Documentation Fine-tuning RoBERTa - CryptoVibe

## 1. Vue d'Ensemble

Ce projet implemente le fine-tuning du modele RoBERTa pour la classification de sentiment des tweets Bitcoin, utilisant un dataset de 19+ millions de tweets.

### 1.1 Caracteristiques Principales

| Caracteristique | Description |
|-----------------|-------------|
| **Modele de base** | `cardiffnlp/twitter-roberta-base-sentiment` |
| **Type** | RobertaForSequenceClassification |
| **Classes** | 2 (Positive, Negative) |
| **Dataset** | ~397,516 tweets Bitcoin |
| **Framework** | PyTorch + Hugging Face Transformers |
| **GPU** | CUDA/GPU supporte (FP16) |

### 1.2 Resultats Obtenus

| Metrique | Objectif | Resultat | Statut |
|----------|----------|----------|--------|
| **Accuracy** | > 75% | 70.1% | Proche |
| **F1-Score macro** | > 0.70 | 0.686 | Proche |
| **Temps entrainement** | - | ~8.8h | 8 epochs |

---

## 2. Architecture

### 2.1 Pipeline d'Entrainement

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE FINE-TUNING RoBERTa                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. DATA LOADING              2. PREPROCESSING                          │
│  ┌─────────────────────┐      ┌─────────────────────┐                   │
│  │ CSV 1M tweets       │ ───▶ │ TextPreprocessor    │                   │
│  │ chunk_size=10000    │      │ - remove_urls       │                   │
│  └─────────────────────┘      │ - handle_mentions   │                   │
│                               │ - handle_hashtags   │                   │
│                               └──────────┬──────────┘                   │
│                                          │                              │
│  3. SPLIT                     4. TOKENIZATION                           │
│  ┌─────────────────────┐      ┌─────────────────────┐                   │
│  │ train: 80%          │      │ RobertaTokenizer    │                   │
│  │ val: 10%            │ ───▶ │ max_length=64       │                   │
│  │ test: 10%           │      │ padding='max_length'│                   │
│  └─────────────────────┘      └──────────┬──────────┘                   │
│                                          │                              │
│  5. TRAINING                  6. EVALUATION                             │
│  ┌─────────────────────┐      ┌─────────────────────┐                   │
│  │ - Mixed Precision   │      │ - Accuracy          │                   │
│  │ - Early Stopping    │ ───▶ │ - F1-Score          │                   │
│  │ - Checkpoints       │      │ - Confusion Matrix  │                   │
│  │ - Gradient Clipping │      └─────────────────────┘                   │
│  └─────────────────────┘                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Structure des Fichiers

```
Finetuning/
├── config.yaml              # Configuration globale
├── data_preparation.py      # Chargement et analyse des donnees
├── preprocessing.py         # Nettoyage et preprocessing texte
├── model_config.py          # Configuration modele RoBERTa
├── train.py                 # Script d'entrainement principal
├── evaluate.py              # Evaluation du modele
├── inference.py             # Predictions sur nouveaux tweets
├── visualize.py             # Visualisations des resultats
├── utils.py                 # Fonctions utilitaires
├── requirements.txt         # Dependances Python
├── roberta-1-1.ipynb        # Notebook Jupyter (meme code)
├── models/                  # Modeles sauvegardes
├── logs/                    # Logs d'entrainement
├── checkpoints/             # Checkpoints intermediaires
├── results/                 # Resultats et visualisations
└── output/                  # Resultats du notebook
    ├── models/
    │   ├── best_model/      # Meilleur modele (F1-score)
    │   ├── final_model/     # Modele final
    │   └── label_mapping.json
    └── results/
        ├── training_metrics.json
        ├── training_curves.png
        ├── confusion_matrix.png
        └── README_INTERPRETATION.md
```

---

## 3. Configuration

### 3.1 Fichier config.yaml

```yaml
# Modele
model:
  name: "cardiffnlp/twitter-roberta-base-sentiment"
  num_labels: 3
  max_length: 64
  freeze_layers: true

# Donnees
data:
  csv_path: "../data/bronze/kaggle/bitcoin_tweets_*.csv"
  sample_size: 1000000
  train_split: 0.8
  val_split: 0.1
  test_split: 0.1
  stratify: true
  chunk_size: 10000

# Preprocessing
preprocessing:
  remove_urls: true
  handle_mentions: true
  handle_hashtags: true
  normalize_spaces: true
  handle_emojis: "keep"

# Entrainement
training:
  batch_size: 2
  learning_rate: 2e-5
  num_epochs: 5
  warmup_steps: 1000
  weight_decay: 0.01
  max_grad_norm: 1.0
  gradient_accumulation_steps: 16
  use_fp16: true
  early_stopping:
    enabled: true
    patience: 3
    monitor: "val_f1"
  use_cuda: true

# Evaluation
evaluation:
  metrics: ["accuracy", "f1", "precision", "recall"]
  save_confusion_matrix: true

# Chemins
paths:
  models_dir: "models"
  logs_dir: "logs"
  checkpoints_dir: "checkpoints"
  results_dir: "results"
  model_save_name: "roberta-bitcoin-sentiment"

# Reproductibilite
reproducibility:
  seed: 42
```

### 3.2 Parametres GPU/Memoire

Pour GPU avec memoire limitee (ex: GTX 1050 2GB):

| Parametre | Valeur | Description |
|-----------|--------|-------------|
| `batch_size` | 2 | Minimum pour 2GB VRAM |
| `gradient_accumulation_steps` | 16 | Simule batch_size=32 |
| `max_length` | 64 | Reduit pour economiser VRAM |
| `use_fp16` | true | Mixed precision (moitie memoire) |
| `freeze_layers` | true | Gele les premieres couches |

---

## 4. Preprocessing

### 4.1 TextPreprocessor

La classe `TextPreprocessor` nettoie les textes:

```python
class TextPreprocessor:
    def clean_text(self, text: str) -> str:
        # 1. Suppression URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)

        # 2. Gestion mentions (@user -> user)
        text = re.sub(r'@(\w+)', r'\1', text)

        # 3. Gestion hashtags (#bitcoin -> bitcoin)
        text = re.sub(r'#(\w+)', r'\1', text)

        # 4. Normalisation espaces
        text = re.sub(r'\s+', ' ', text)

        # 5. Gestion emojis (keep/remove/convert)
        # ...

        return text.strip()
```

### 4.2 LabelEncoder

```python
# Mapping des labels
label_mapping = {
    'Negative': 0,
    'Positive': 1
}
# Note: Le modele original supporte 3 classes mais
# le dataset utilise est binaire (Positive/Negative)
```

---

## 5. Entrainement

### 5.1 Commandes

```bash
# Entrainement complet
python Finetuning/train.py

# Ou via notebook
jupyter notebook Finetuning/roberta-1-1.ipynb
```

### 5.2 Classe Trainer

```python
class Trainer:
    def train(self):
        # 1. Preparation des donnees
        train_df, val_df, test_df = self.prepare_data()

        # 2. Initialisation modele
        self.model_wrapper = RobertaModelConfig(
            model_name=self.model_config['name'],
            num_labels=self.model_config['num_labels'],
            use_cuda=True
        )

        # 3. Creation DataLoaders
        train_loader, val_loader = self.create_dataloaders(train_df, val_df)

        # 4. Boucle d'entrainement
        for epoch in range(1, num_epochs + 1):
            train_loss = self.train_epoch(...)
            val_loss, val_acc, val_f1 = self.validate(...)

            # Early stopping
            if patience_counter >= patience:
                break

            # Sauvegarde checkpoint
            self.save_checkpoint(model, epoch, val_f1, is_best)
```

### 5.3 Mixed Precision (FP16)

```python
# Activation FP16 pour economiser memoire GPU
scaler = torch.cuda.amp.GradScaler()

with torch.cuda.amp.autocast():
    outputs = model(input_ids, attention_mask, labels)
    loss = outputs.loss

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

---

## 6. Resultats d'Entrainement

### 6.1 Evolution des Metriques

#### Loss

| Epoch | Train Loss | Val Loss |
|-------|------------|----------|
| 1 | 0.538 | 0.668 |
| 2 | 0.464 | 0.712 |
| 3 | 0.419 | 0.627 |
| 4 | 0.383 | 0.698 |
| 5 | 0.350 | 0.732 |
| 6 | 0.324 | 0.738 |
| 7 | 0.305 | 0.777 |
| 8 | 0.292 | 0.770 |

#### Accuracy et F1-Score

| Epoch | Val Accuracy | Val F1-Score |
|-------|--------------|--------------|
| 1 | 56.1% | 0.561 |
| 2 | 62.0% | 0.618 |
| 3 | 67.1% | 0.661 |
| 4 | 67.4% | 0.664 |
| 5 | 68.3% | 0.672 |
| 6 | 69.0% | 0.678 |
| 7 | 69.9% | 0.684 |
| 8 | **70.1%** | **0.686** |

### 6.2 Visualisations

Les fichiers suivants sont generes dans `output/results/`:

- **`training_curves.png`**: Courbes loss, accuracy, F1-score
- **`confusion_matrix.png`**: Matrice de confusion
- **`training_metrics.json`**: Metriques detaillees

---

## 7. Evaluation

### 7.1 Commande

```bash
python Finetuning/evaluate.py
```

### 7.2 Metriques Calculees

| Metrique | Valeur |
|----------|--------|
| **Accuracy** | 70.1% |
| **F1-Score (macro)** | 0.686 |
| **F1-Score (weighted)** | - |
| **Precision (macro)** | - |
| **Recall (macro)** | - |

### 7.3 Interpretation

**Points Positifs:**
1. Amelioration constante sur accuracy et F1-score
2. Convergence vers une solution stable
3. Performance acceptable pour classification binaire

**Points d'Amelioration:**
1. **Overfitting** visible apres epoch 2-3 (val loss augmente)
2. Performance legerement sous les objectifs (75% accuracy)
3. Early stopping pourrait etre plus agressif

---

## 8. Inference

### 8.1 Classe SentimentPredictor

```python
from Finetuning.inference import SentimentPredictor

# Charger le modele
predictor = SentimentPredictor(
    model_path="output/models/best_model",
    use_cuda=True
)

# Prediction simple
result = predictor.predict("Bitcoin is going to the moon!")
print(result)
# {'label': 'positive', 'confidence': 0.85}

# Prediction avec probabilites
result = predictor.predict("Bitcoin crashed today", return_proba=True)
print(result)
# {
#     'label': 'negative',
#     'confidence': 0.78,
#     'probabilities': {'positive': 0.22, 'negative': 0.78}
# }

# Prediction batch
texts = ["Tweet 1", "Tweet 2", "Tweet 3"]
predictions = predictor.predict_batch(texts, batch_size=32)
```

### 8.2 Exemple Complet

```python
import logging
logging.basicConfig(level=logging.INFO)

predictor = SentimentPredictor(use_cuda=False)

test_texts = [
    "Bitcoin is going to the moon!",
    "I lost all my money in crypto",
    "Bitcoin price is stable today"
]

print("="*60)
print("SENTIMENT ANALYSIS EXAMPLES")
print("="*60)

for text in test_texts:
    result = predictor.predict(text, return_proba=True)
    print(f"\nText: {text}")
    print(f"Sentiment: {result['label']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Probabilities: {result['probabilities']}")
```

---

## 9. Installation

### 9.1 Prerequis

- Python 3.8+
- GPU CUDA (recommande, 8GB+ VRAM)
- 10GB+ espace disque

### 9.2 Installation des Dependances

```bash
pip install -r Finetuning/requirements.txt
```

### 9.3 Installation PyTorch avec CUDA

```bash
# Pour CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Pour CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 9.4 Verification CUDA

```python
import torch
print(torch.cuda.is_available())      # True
print(torch.cuda.get_device_name(0))  # Nom du GPU
```

---

## 10. Optimisations

### 10.1 GPU avec Memoire Limitee

```yaml
# config.yaml
training:
  batch_size: 8         # Reduire (16 -> 8)
  gradient_accumulation_steps: 4  # Augmenter
  use_fp16: true        # Activer mixed precision

model:
  max_length: 64        # Reduire (128 -> 64)
  freeze_layers: true   # Geler couches basses
```

### 10.2 Ameliorer la Performance

1. **Early Stopping**: Arreter quand val_loss stagne
2. **Dropout**: Augmenter (0.1 -> 0.2)
3. **Learning Rate**: Tester 1e-5 (plus bas)
4. **Data Augmentation**: Paraphrase, back-translation

### 10.3 Dataset Plus Grand

```yaml
# config.yaml
data:
  sample_size: null     # Utiliser tout le dataset
  chunk_size: 50000     # Augmenter pour lecture rapide
```

---

## 11. Comparaison des Approches

| Critere | VADER Hybride | RoBERTa Fine-tune |
|---------|---------------|-------------------|
| **Accuracy** | 69.80% | **70.1%** |
| **F1-Score macro** | 0.54 | **0.686** |
| **Temps entrainement** | ~5 min | ~8.8h |
| **Temps inference** | ~1ms/tweet | ~50ms/tweet |
| **GPU requis** | Non | Recommande |
| **Taille modele** | ~100KB | ~500MB |
| **Cas ambigus** | Faible | **Meilleur** |
| **Sarcasme** | Faible | **Meilleur** |

**Conclusion:** RoBERTa offre de meilleures performances mais est plus lourd. VADER est plus adapte pour des applications temps-reel a grande echelle.

---

## 12. Troubleshooting

### CUDA Not Available

```python
# Verifier installation
import torch
print(torch.cuda.is_available())  # False?

# Solutions:
# 1. Verifier drivers NVIDIA
# 2. Reinstaller PyTorch avec CUDA
# 3. Le code bascule automatiquement sur CPU
```

### GPU Memory Error

```yaml
# Reduire batch_size dans config.yaml
training:
  batch_size: 2          # Minimum
  use_fp16: true         # Activer FP16
  gradient_accumulation_steps: 16
```

### Dataset Trop Grand

```yaml
# Limiter le sample
data:
  sample_size: 500000    # 500K au lieu de 1M
```

### Erreur Unicode (Windows)

```bash
set PYTHONIOENCODING=utf-8
python Finetuning/train.py
```

---

## 13. Fichiers de Sortie

### 13.1 Modeles

| Fichier | Description |
|---------|-------------|
| `models/best_model/` | Meilleur modele (F1-score) |
| `models/final_model/` | Modele final (dernier epoch) |
| `models/label_mapping.json` | Mapping des labels |

### 13.2 Checkpoints

| Fichier | Description |
|---------|-------------|
| `checkpoints/checkpoint_epoch_N.pt` | Checkpoint par epoch |
| `checkpoints/best_model.pt` | Meilleur checkpoint |

### 13.3 Resultats

| Fichier | Description |
|---------|-------------|
| `results/training_metrics.json` | Metriques d'entrainement |
| `results/evaluation_results.json` | Resultats d'evaluation |
| `results/training_curves.png` | Courbes d'entrainement |
| `results/confusion_matrix.png` | Matrice de confusion |
| `results/train_split.csv` | Donnees d'entrainement |
| `results/val_split.csv` | Donnees de validation |
| `results/test_split.csv` | Donnees de test |

---

## 14. References

| Ressource | Lien |
|-----------|------|
| Hugging Face Transformers | [huggingface.co/docs/transformers](https://huggingface.co/docs/transformers) |
| RoBERTa Paper | [arxiv.org/abs/1907.11692](https://arxiv.org/abs/1907.11692) |
| PyTorch Documentation | [pytorch.org/docs](https://pytorch.org/docs/) |
| Cardiff NLP Models | [huggingface.co/cardiffnlp](https://huggingface.co/cardiffnlp) |

---

## 15. Changelog

| Version | Date | Modifications |
|---------|------|---------------|
| 1.0 | 2024-11 | Version initiale avec RoBERTa fine-tune |
| 1.1 | 2024-11 | Ajout support 2 classes (binaire) |

