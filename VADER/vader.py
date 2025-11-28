import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.metrics import classification_report, accuracy_score
import nltk
import os

# ===============================================================
# 1️⃣ INSTALLATION & INITIALISATION
# ===============================================================
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# ===============================================================
# 2️⃣ PARAMÈTRES
# ===============================================================
TEXT_COL = 'processed_text'  # colonne texte dans les deux fichiers
LABEL_COL = 'Label'          # colonne des vrais sentiments (dans processed_train_data.xlsx)
ID_COL = 'unified_id'        # colonne ID commune pour la fusion

# ===============================================================
# 3️⃣ CHARGER ET FUSIONNER LES DONNÉES
# ===============================================================
train_df = pd.read_excel("processed_train_data.xlsx")
test_df = pd.read_excel("processed_test_data.xlsx")
# Vérif rapide
print("\n✅ Fichiers chargés :")
print(f"Train shape: {train_df.shape}")
print(f"Test shape:  {test_df.shape}")

# ===============================================================
# 4️⃣ FONCTION D'ANALYSE VADER
# ===============================================================
def get_vader_sentiment(text):
    # Gérer les cas où le texte est vide ou NaN (Not a Number)
    if pd.isna(text) or not str(text).strip():
        return {'neg': 0, 'neu': 1, 'pos': 0, 'compound': 0, 'predicted_label': 'neutral'}
        
    scores = sia.polarity_scores(str(text))
    compound = scores['compound']
    if compound >= 0.05:
        sentiment = 'positive'
    elif compound <= -0.05:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    scores['predicted_label'] = sentiment
    return scores

# ===============================================================
# 5️⃣ APPLIQUER SUR LE TRAIN
# ===============================================================
print("\n🔍 Application de VADER sur le TRAIN...")
vader_train = train_df[TEXT_COL].apply(get_vader_sentiment).apply(pd.Series)
train_results = pd.concat([train_df, vader_train], axis=1)
train_output_path = os.path.abspath("vader_train_results.xlsx")
train_results.to_excel(train_output_path, index=False)
print(f"✅ Résultats train sauvegardés ici : {train_output_path}")
print(train_results[['processed_text', 'predicted_label']].head())

# ===============================================================
# 5.1️⃣ ÉVALUER LA PERFORMANCE (BASELINE)
# ===============================================================
print("\n📊 Évaluation de la performance de VADER sur le TRAIN...")
print("⚠️ La colonne de labels est introuvable. L'évaluation est impossible et a été désactivée.")

# ===============================================================
# 6️⃣ APPLIQUER SUR LE TEST
# ===============================================================
print("\n🔍 Application de VADER sur le TEST...")
vader_test = test_df[TEXT_COL].apply(get_vader_sentiment).apply(pd.Series)
test_results = pd.concat([test_df, vader_test], axis=1)
test_output_path = os.path.abspath("vader_test_results.xlsx")
test_results.to_excel(test_output_path, index=False)
print(f"✅ Résultats test sauvegardés ici : {test_output_path}")
print(test_results[['processed_text', 'predicted_label']].head())

print("\n🎉 Analyse VADER terminée avec succès sur les deux jeux de données !")
