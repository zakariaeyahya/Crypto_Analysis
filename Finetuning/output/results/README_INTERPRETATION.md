# 📊 Interprétation des Résultats du Fine-tuning RoBERTa

Ce document présente une analyse détaillée des résultats obtenus lors du fine-tuning du modèle RoBERTa pour l'analyse de sentiment des tweets Bitcoin.

## 📋 Vue d'ensemble

- **Modèle** : RoBERTa (RobertaForSequenceClassification)
- **Dataset** : ~397,516 tweets Bitcoin
- **Classes** : 2 classes (Negative, Positive)
- **Nombre d'epochs** : 8
- **Temps d'entraînement** : ~8.8 heures (31,722 secondes)

## 📈 Métriques d'entraînement

### Évolution de la Loss

#### Training Loss
La loss d'entraînement diminue régulièrement de **0.538** (epoch 1) à **0.292** (epoch 8), indiquant que le modèle apprend progressivement à classifier les sentiments.

| Epoch | Training Loss |
|-------|---------------|
| 1     | 0.538         |
| 2     | 0.464         |
| 3     | 0.419         |
| 4     | 0.383         |
| 5     | 0.350         |
| 6     | 0.324         |
| 7     | 0.305         |
| 8     | 0.292         |

**Interprétation** : La diminution constante de la loss d'entraînement montre que le modèle continue d'apprendre. Cependant, la perte de validation augmente après l'epoch 2, ce qui suggère un début d'overfitting.

#### Validation Loss
La loss de validation présente une évolution plus irrégulière :

| Epoch | Validation Loss |
|-------|-----------------|
| 1     | 0.668           |
| 2     | 0.712 ⬆️        |
| 3     | 0.627 ⬇️        |
| 4     | 0.698 ⬆️        |
| 5     | 0.732 ⬆️        |
| 6     | 0.738 ⬆️        |
| 7     | 0.777 ⬆️        |
| 8     | 0.770 ⬇️        |

**Interprétation** : 
- La validation loss augmente globalement après l'epoch 2, ce qui indique un **overfitting**.
- Le meilleur modèle aurait probablement été obtenu à l'epoch 3 (validation loss = 0.627).
- L'écart croissant entre training loss et validation loss confirme l'overfitting.

### Évolution de l'Accuracy

L'accuracy de validation s'améliore progressivement :

| Epoch | Validation Accuracy |
|-------|---------------------|
| 1     | 56.1%               |
| 2     | 62.0%               |
| 3     | 67.1%               |
| 4     | 67.4%               |
| 5     | 68.3%               |
| 6     | 69.0%               |
| 7     | 69.9%               |
| 8     | **70.1%**          |

**Interprétation** :
- L'accuracy augmente de manière constante, passant de 56.1% à 70.1%.
- L'amélioration ralentit après l'epoch 3, suggérant que le modèle atteint un plateau.
- L'accuracy finale de **70.1%** est acceptable mais pourrait être améliorée.

### Évolution du F1-Score

Le F1-score macro suit une évolution similaire à l'accuracy :

| Epoch | Validation F1-Score |
|-------|---------------------|
| 1     | 0.561               |
| 2     | 0.618               |
| 3     | 0.661               |
| 4     | 0.664               |
| 5     | 0.672               |
| 6     | 0.678               |
| 7     | 0.684               |
| 8     | **0.686**          |

**Interprétation** :
- Le F1-score final de **0.686** est légèrement en dessous de l'objectif de 0.70.
- L'amélioration ralentit significativement après l'epoch 3.
- Le meilleur F1-score est atteint à l'epoch 8 : **0.686**.

## 🎯 Résultats finaux

### Métriques principales

- **Meilleur F1-Score (validation)** : **0.686** (68.6%)
- **Accuracy finale (validation)** : **70.1%**
- **Training Loss finale** : 0.292
- **Validation Loss finale** : 0.770

### Comparaison avec les objectifs

| Métrique | Objectif | Atteint | Statut |
|----------|----------|---------|--------|
| Accuracy | > 75% | 70.1% | ⚠️ En dessous |
| F1-Score macro | > 0.70 | 0.686 | ⚠️ Légèrement en dessous |
| F1-Score par classe | > 0.65 | À vérifier | ⏳ À analyser |

## 🔍 Analyse des performances

### Points positifs ✅

1. **Amélioration constante** : Le modèle s'améliore régulièrement sur les métriques d'accuracy et F1-score.
2. **Convergence** : Le modèle converge vers une solution stable.
3. **Performance acceptable** : 70.1% d'accuracy et 68.6% de F1-score sont des résultats raisonnables pour une classification binaire de sentiment.

### Points d'amélioration ⚠️

1. **Overfitting** : 
   - La validation loss augmente après l'epoch 2-3.
   - L'écart entre training loss et validation loss s'agrandit.
   - **Recommandation** : Utiliser early stopping ou régularisation plus forte.

2. **Performance sous les objectifs** :
   - L'accuracy (70.1%) est en dessous de l'objectif de 75%.
   - Le F1-score (0.686) est légèrement en dessous de 0.70.
   - **Recommandation** : Tester différents hyperparamètres, augmenter la taille du dataset, ou essayer data augmentation.

3. **Optimisation des epochs** :
   - Le meilleur modèle aurait pu être obtenu plus tôt (epoch 3).
   - **Recommandation** : Implémenter early stopping basé sur validation loss.

## 📊 Visualisations disponibles

Les fichiers suivants sont disponibles dans ce dossier :

- **`training_curves.png`** : Courbes d'évolution de la loss, accuracy et F1-score
- **`confusion_matrix.png`** : Matrice de confusion sur le test set
- **`training_metrics.json`** : Métriques détaillées au format JSON

## 🔧 Recommandations pour améliorer les performances

### 1. Gestion de l'overfitting

- **Early stopping** : Arrêter l'entraînement quand la validation loss cesse de diminuer.
- **Dropout** : Augmenter le taux de dropout (actuellement 0.1).
- **Weight decay** : Augmenter le weight decay pour plus de régularisation.
- **Data augmentation** : Paraphrase, back-translation, ou synonym replacement.

### 2. Optimisation des hyperparamètres

- **Learning rate** : Tester des learning rates plus faibles (1e-5) ou utiliser un scheduler adaptatif.
- **Batch size** : Tester différentes tailles de batch.
- **Max length** : Analyser si 128 tokens est optimal pour les tweets.

### 3. Amélioration des données

- **Plus de données** : Utiliser un échantillon plus large du dataset complet.
- **Équilibrage des classes** : Vérifier et corriger le déséquilibre si présent.
- **Nettoyage** : Améliorer le preprocessing des textes.

### 4. Architecture du modèle

- **Modèle plus grand** : Tester `roberta-large` si les ressources le permettent.
- **Modèle spécialisé** : Utiliser `cardiffnlp/twitter-roberta-base-sentiment` qui est pré-entraîné sur Twitter.

## 📁 Fichiers de résultats

### Modèles sauvegardés

- **`../models/best_model/`** : Meilleur modèle basé sur validation F1-score
- **`../models/final_model/`** : Modèle final après 8 epochs
- **`../models/label_mapping.json`** : Mapping des labels (Negative: 0, Positive: 1)

### Splits de données

- **`train_split.csv`** : Dataset d'entraînement (~397k tweets)
- **`val_split.csv`** : Dataset de validation
- **`test_split.csv`** : Dataset de test

## 🎓 Conclusion

Le modèle RoBERTa fine-tuné atteint des performances **acceptables** avec :
- **70.1% d'accuracy**
- **68.6% de F1-score macro**

Cependant, il y a des signes d'**overfitting** et les performances sont **légèrement en dessous des objectifs**. Les recommandations ci-dessus peuvent aider à améliorer les résultats.

Le modèle est **utilisable en production** pour une classification basique de sentiment, mais des améliorations sont possibles avec les optimisations suggérées.

---

**Date de génération** : Résultats obtenus après l'exécution de `roberta-1-1.ipynb`  
**Modèle de base** : RoBERTa (RobertaForSequenceClassification)  
**Configuration** : Voir `../models/best_model/config.json`

