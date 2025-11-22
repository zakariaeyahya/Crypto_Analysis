# 📊 RoBERTa Fine-tuning Results Interpretation

This document presents a detailed analysis of the results obtained during fine-tuning of the RoBERTa model for Bitcoin tweet sentiment analysis.

## 📋 Overview

- **Model**: RoBERTa (RobertaForSequenceClassification)
- **Dataset**: ~397,516 Bitcoin tweets
- **Classes**: 2 classes (Negative, Positive)
- **Number of epochs**: 8
- **Training time**: ~8.8 hours (31,722 seconds)

## 📈 Training Metrics

### Loss Evolution

#### Training Loss
Training loss decreases steadily from **0.538** (epoch 1) to **0.292** (epoch 8), indicating that the model is progressively learning to classify sentiments.

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

**Interpretation**: The constant decrease in training loss shows that the model continues to learn. However, validation loss increases after epoch 2, suggesting the beginning of overfitting.

#### Validation Loss
Validation loss shows a more irregular evolution:

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

**Interpretation**: 
- Validation loss increases overall after epoch 2, indicating **overfitting**.
- The best model would likely have been obtained at epoch 3 (validation loss = 0.627).
- The growing gap between training loss and validation loss confirms overfitting.

### Accuracy Evolution

Validation accuracy improves progressively:

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

**Interpretation**:
- Accuracy increases steadily, from 56.1% to 70.1%.
- Improvement slows after epoch 3, suggesting the model reaches a plateau.
- Final accuracy of **70.1%** is acceptable but could be improved.

### F1-Score Evolution

Macro F1-score follows a similar evolution to accuracy:

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

**Interpretation**:
- Final F1-score of **0.686** is slightly below the target of 0.70.
- Improvement slows significantly after epoch 3.
- Best F1-score is reached at epoch 8: **0.686**.

## 🎯 Final Results

### Main Metrics

- **Best F1-Score (validation)**: **0.686** (68.6%)
- **Final Accuracy (validation)**: **70.1%**
- **Final Training Loss**: 0.292
- **Final Validation Loss**: 0.770

### Comparison with Objectives

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Accuracy | > 75% | 70.1% | ⚠️ Below target |
| F1-Score macro | > 0.70 | 0.686 | ⚠️ Slightly below |
| F1-Score per class | > 0.65 | To verify | ⏳ To analyze |

## 🔍 Performance Analysis

### Positive Points ✅

1. **Constant improvement**: Model improves regularly on accuracy and F1-score metrics.
2. **Convergence**: Model converges to a stable solution.
3. **Acceptable performance**: 70.1% accuracy and 68.6% F1-score are reasonable results for binary sentiment classification.

### Improvement Points ⚠️

1. **Overfitting**: 
   - Validation loss increases after epoch 2-3.
   - Gap between training loss and validation loss widens.
   - **Recommendation**: Use early stopping or stronger regularization.

2. **Performance below objectives**:
   - Accuracy (70.1%) is below the 75% target.
   - F1-score (0.686) is slightly below 0.70.
   - **Recommendation**: Test different hyperparameters, increase dataset size, or try data augmentation.

3. **Epoch optimization**:
   - Best model could have been obtained earlier (epoch 3).
   - **Recommendation**: Implement early stopping based on validation loss.

## 📊 Available Visualizations

The following files are available in this directory:

- **`training_curves.png`**: Evolution curves of loss, accuracy and F1-score
- **`confusion_matrix.png`**: Confusion matrix on test set
- **`training_metrics.json`**: Detailed metrics in JSON format

## 🔧 Recommendations to Improve Performance

### 1. Overfitting Management

- **Early stopping**: Stop training when validation loss stops decreasing.
- **Dropout**: Increase dropout rate (currently 0.1).
- **Weight decay**: Increase weight decay for more regularization.
- **Data augmentation**: Paraphrase, back-translation, or synonym replacement.

### 2. Hyperparameter Optimization

- **Learning rate**: Test lower learning rates (1e-5) or use adaptive scheduler.
- **Batch size**: Test different batch sizes.
- **Max length**: Analyze if 128 tokens is optimal for tweets.

### 3. Data Improvement

- **More data**: Use a larger sample from the complete dataset.
- **Class balancing**: Check and correct imbalance if present.
- **Cleaning**: Improve text preprocessing.

### 4. Model Architecture

- **Larger model**: Test `roberta-large` if resources allow.
- **Specialized model**: Use `cardiffnlp/twitter-roberta-base-sentiment` which is pre-trained on Twitter.

## 📁 Result Files

### Saved Models

- **`../models/best_model/`**: Best model based on validation F1-score
- **`../models/final_model/`**: Final model after 8 epochs
- **`../models/label_mapping.json`**: Label mapping (Negative: 0, Positive: 1)

### Data Splits

- **`train_split.csv`**: Training dataset (~397k tweets)
- **`val_split.csv`**: Validation dataset
- **`test_split.csv`**: Test dataset

## 🎓 Conclusion

The fine-tuned RoBERTa model achieves **acceptable** performance with:
- **70.1% accuracy**
- **68.6% macro F1-score**

However, there are signs of **overfitting** and performance is **slightly below objectives**. The recommendations above can help improve results.

The model is **usable in production** for basic sentiment classification, but improvements are possible with the suggested optimizations.

---

**Generation date**: Results obtained after execution of `roberta-1-1.ipynb`  
**Base model**: RoBERTa (RobertaForSequenceClassification)  
**Configuration**: See `../models/best_model/config.json`
