# Documentation VADER Hybride - CryptoVibe

## 1. Vue d'Ensemble

Le projet VADER Hybride implemente une analyse de sentiment specifiquement adaptee aux tweets sur les cryptomonnaies. Les outils NLP standards (comme VADER par defaut) echouent souvent a capturer le sentiment du jargon crypto (ex: "HODL", "To the moon", "Rekt").

### 1.1 Approche Hybride

L'approche hybride combine deux methodes:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        VADER HYBRIDE                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────┐     ┌─────────────────────┐                    │
│  │ LEXIQUE AUTOMATIQUE │     │  LEXIQUE MANUEL     │                    │
│  │ (Apprentissage)     │     │  (Expert Crypto)    │                    │
│  │                     │     │                     │                    │
│  │ - 4,557 mots        │     │ - 16 termes cles    │                    │
│  │ - Score statistique │     │ - Score expert      │                    │
│  │ - Frequence > 50    │     │ - Prioritaire       │                    │
│  └──────────┬──────────┘     └──────────┬──────────┘                    │
│             │                           │                               │
│             └───────────┬───────────────┘                               │
│                         ▼                                               │
│              ┌─────────────────────┐                                    │
│              │  VADER AMELIORE     │                                    │
│              │  (Lexique combine)  │                                    │
│              └─────────────────────┘                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Caracteristiques

| Caracteristique | Description |
|-----------------|-------------|
| **Type** | Analyse lexicale basee sur regles |
| **Dataset** | 1M tweets Bitcoin (Kaggle) |
| **Classes** | Binaire (Positive/Negative) |
| **Lexique** | 4,557 mots + 16 termes experts |
| **Accuracy** | 69.80% |

---

## 2. Structure du Projet

```
vaderr/
├── vader.ipynb                 # Notebook principal (train + eval)
├── crypto_lexicon_final.json   # Lexique pre-entraine (poids du modele)
├── train_full.csv              # Dataset entrainement (70%)
├── val_full.csv                # Dataset validation (15%)
├── test_full.csv               # Dataset test (15%)
└── README.md.txt               # Documentation
```

---

## 3. Pipeline d'Entrainement

### 3.1 Etapes du Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE VADER HYBRIDE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. CHARGEMENT        2. NETTOYAGE         3. SPLIT                     │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐              │
│  │ Kaggle CSV  │ ───▶ │ clean_tweet │ ───▶ │ 70/15/15    │              │
│  │ 1M tweets   │      │ (regex)     │      │ stratifie   │              │
│  └─────────────┘      └─────────────┘      └─────────────┘              │
│                                                   │                      │
│                                                   ▼                      │
│  4. GENERATION LEXIQUE                    5. FUSION                     │
│  ┌──────────────────────────┐            ┌─────────────┐                │
│  │ Pour chaque mot:         │            │ auto_lexicon│                │
│  │ - ratio = pos / total    │    ───▶    │     +       │                │
│  │ - si ratio > 75%: +score │            │ manual_lexicon              │
│  │ - si ratio < 25%: -score │            └─────────────┘                │
│  └──────────────────────────┘                   │                       │
│                                                 ▼                       │
│                                    6. EVALUATION SUR TEST               │
│                                    ┌─────────────┐                      │
│                                    │ 148,664     │                      │
│                                    │ predictions │                      │
│                                    └─────────────┘                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Nettoyage du Texte

La fonction `clean_tweet()` effectue les operations suivantes:

```python
def clean_tweet(text):
    # 1. Suppression des URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # 2. Suppression des mentions (@username)
    text = re.sub(r'@\w+', '', text)

    # 3. Suppression des hashtags (#hashtag)
    text = re.sub(r'#\w+', '', text)

    # 4. Suppression caracteres speciaux
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    # 5. Conversion en minuscules
    text = text.lower()

    # 6. Normalisation espaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text
```

### 3.3 Generation du Lexique Automatique

**Algorithme:**

```
Pour chaque mot dans le corpus d'entrainement:
    1. Compter occurrences dans tweets positifs (p)
    2. Compter occurrences dans tweets negatifs (n)
    3. Calculer ratio = p / (p + n)

    Si total < 50: ignorer (mot rare)
    Si ratio > 0.75: score = +2.0 + (ratio * 2.0)  # Max +4.0
    Si ratio < 0.25: score = -2.0 - ((1-ratio) * 2.0)  # Max -4.0
```

**Filtres:**
- Mots de moins de 3 caracteres ignores
- Stop words (anglais) ignores
- Frequence minimum: 50 occurrences

**Resultat:** 4,557 mots avec scores de sentiment

### 3.4 Lexique Manuel Expert

Le lexique manuel contient les termes crypto specifiques:

| Terme | Score | Description |
|-------|-------|-------------|
| hodl | +3.5 | Argot pour "hold" (garder) |
| moon | +4.0 | "To the moon" - hausse extreme |
| bullish | +3.5 | Sentiment haussier |
| ath | +3.5 | All-Time High (record) |
| pump | +2.5 | Hausse rapide |
| bearish | -3.5 | Sentiment baissier |
| fud | -3.0 | Fear, Uncertainty, Doubt |
| dump | -3.5 | Baisse rapide/vente massive |
| scam | -4.0 | Arnaque |
| rekt | -4.0 | "Wrecked" - grosse perte |
| btc | +1.0 | Bitcoin (neutre positif) |
| bitcoin | +1.0 | Bitcoin |
| buy | +2.5 | Achat |
| long | +2.5 | Position longue |
| short | -2.5 | Position courte |
| sell | -2.5 | Vente |

---

## 4. Utilisation

### 4.1 Installation

```bash
pip install pandas numpy nltk scikit-learn tqdm
```

### 4.2 Inference (Prediction)

```python
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Telecharger VADER si necessaire
nltk.download('vader_lexicon', quiet=True)

# Initialiser VADER
sid = SentimentIntensityAnalyzer()

# Charger le lexique crypto
with open('crypto_lexicon_final.json', 'r') as f:
    crypto_lexicon = json.load(f)

# Mettre a jour VADER avec le vocabulaire crypto
sid.lexicon.update(crypto_lexicon)

# Prediction
def predict_sentiment(text):
    score = sid.polarity_scores(text)['compound']
    return "Positive" if score > 0 else "Negative"

# Test
texts = [
    "Just bought the dip, extremely bullish on BTC! HODL.",
    "This project is a total scam, I got rekt.",
    "Bitcoin is stable today."
]

for text in texts:
    scores = sid.polarity_scores(text)
    sentiment = "Positive" if scores['compound'] > 0 else "Negative"
    print(f"Text: '{text}'")
    print(f"Score: {scores['compound']:.4f} | Sentiment: {sentiment}\n")
```

### 4.3 Sortie Attendue

```
Text: 'Just bought the dip, extremely bullish on BTC! HODL.'
Score: 0.8562 | Sentiment: Positive

Text: 'This project is a total scam, I got rekt.'
Score: -0.7650 | Sentiment: Negative

Text: 'Bitcoin is stable today.'
Score: 0.2500 | Sentiment: Positive
```

---

## 5. Resultats d'Evaluation

### 5.1 Metriques Globales

| Metrique | Valeur |
|----------|--------|
| **Accuracy Globale** | **69.80%** |
| **Dataset Test** | 148,664 tweets |
| **Seuil** | 0.0 (compound score) |

### 5.2 Metriques par Classe

| Classe | Precision | Recall | F1-Score | Support |
|--------|-----------|--------|----------|---------|
| **Negative** | 0.42 | 0.19 | 0.26 | 42,047 |
| **Positive** | 0.74 | 0.90 | 0.81 | 106,617 |
| **Macro avg** | 0.58 | 0.54 | 0.54 | 148,664 |
| **Weighted avg** | 0.65 | 0.70 | 0.66 | 148,664 |

### 5.3 Matrice de Confusion

```
                Predit Neg    Predit Pos
Vrai Neg         8,058         33,989
Vrai Pos        10,904         95,713
```

### 5.4 Interpretation

**Points Forts:**
- Excellent recall pour la classe Positive (0.90)
- Bonne precision pour la classe Positive (0.74)
- Modele tres efficace pour detecter le "hype" et l'optimisme

**Points Faibles:**
- Faible recall pour la classe Negative (0.19)
- Le modele a du mal avec la negativite subtile et le sarcasme
- Desequilibre des classes (67.5% Positive vs 32.5% Negative)

---

## 6. Comparaison avec RoBERTa

| Critere | VADER Hybride | RoBERTa Fine-tune |
|---------|---------------|-------------------|
| **Accuracy** | 69.80% | 70.1% |
| **F1-Score** | 0.54 (macro) | 0.686 (macro) |
| **Temps inference** | ~1ms/tweet | ~50ms/tweet |
| **GPU requis** | Non | Recommande |
| **Entrainement** | Minutes | Heures |
| **Interpretabilite** | Haute | Moyenne |
| **Sarcasme/Ironie** | Faible | Meilleur |

**Conclusion:** VADER Hybride est plus rapide et plus leger, mais RoBERTa offre de meilleures performances F1, notamment pour les cas ambigus.

---

## 7. Fichiers de Donnees

### 7.1 Format du Lexique (JSON)

```json
{
  "bullish": 3.5,
  "hodl": 3.5,
  "scam": -4.0,
  "rekt": -4.0,
  "blockchain": 2.1,
  "crash": -3.2,
  ...
}
```

### 7.2 Format des CSV

| Colonne | Type | Description |
|---------|------|-------------|
| `cleaned_text` | string | Texte nettoye |
| `label` | int | 0=Negative, 1=Positive |

---

## 8. Configuration

### 8.1 Parametres d'Entrainement

| Parametre | Valeur | Description |
|-----------|--------|-------------|
| `chunk_size` | 100,000 | Taille des chunks pour lecture |
| `probs` | [0.70, 0.15, 0.15] | Split train/val/test |
| `min_frequency` | 50 | Frequence min pour lexique |
| `ratio_positive` | > 0.75 | Seuil pour score positif |
| `ratio_negative` | < 0.25 | Seuil pour score negatif |
| `threshold` | 0.0 | Seuil compound pour classification |

---

## 9. Troubleshooting

### Erreur: "Could not find 'train_full.csv'"

```bash
# Regenerer les fichiers de split
# Executer les cellules 1-5 du notebook vader.ipynb
```

### Erreur: "crypto_lexicon_final.json not found"

```bash
# Regenerer le lexique
# Executer la cellule 6 du notebook vader.ipynb
```

### Performance Faible sur Textes Negatifs

- Le modele est biaise vers le positif (67.5% du dataset)
- Solutions:
  1. Sous-echantillonner la classe positive
  2. Augmenter les poids des termes negatifs dans le lexique manuel
  3. Ajuster le seuil de classification (ex: 0.1 au lieu de 0.0)

---

## 10. References

| Ressource | Lien |
|-----------|------|
| NLTK VADER | [nltk.org](https://www.nltk.org/howto/sentiment.html) |
| Dataset Kaggle | [Bitcoin Tweets 16M](https://www.kaggle.com/datasets) |
| Paper VADER | [VADER: A Parsimonious Rule-based Model](https://ojs.aaai.org/index.php/ICWSM/article/view/14550) |

---

## 11. Changelog

| Version | Date | Modifications |
|---------|------|---------------|
| 1.0 | 2024-11 | Version initiale avec lexique hybride |

