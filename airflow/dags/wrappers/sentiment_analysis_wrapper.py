"""
Simple Sentiment Analysis Wrapper - KISS principle
Reads from cleaned_reddit_dataset.csv and saves to master_dataset.csv
"""
import logging
import pandas as pd
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def analyze_sentiment_batch(texts, model, tokenizer, device, batch_size=32):
    """Analyze sentiment for a batch of texts"""
    # Import torch here (lazy import)
    import torch

    sentiments = []
    confidences = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        # Tokenize
        inputs = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(device)

        # Predict
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            predictions = torch.argmax(probs, dim=-1)
            confidences_batch = torch.max(probs, dim=-1).values

        # Convert to sentiment labels
        label_map = {0: "negative", 1: "neutral", 2: "positive"}
        for pred, conf in zip(predictions.cpu().numpy(), confidences_batch.cpu().numpy()):
            sentiments.append(label_map.get(pred, "neutral"))
            confidences.append(float(conf))

    return sentiments, confidences


def run_sentiment_analysis(**context):
    """
    Main function: Add sentiment column to master dataset

    Logic:
    1. Load data/silver/reddit/cleaned_reddit_dataset.csv (INPUT)
    2. Check if 'sentiment' column exists
    3. If NO → Analyze ALL rows
    4. If YES → Analyze only NEW rows (using checkpoint)
    5. Save updated CSV to data/silver/consolidation/master_dataset.csv (OUTPUT)
    """
    logger.info("=" * 60)
    logger.info("SENTIMENT ANALYSIS - Incremental Update")
    logger.info("=" * 60)

    # Paths
    # INPUT: Read from cleaned Reddit dataset
    input_csv_path = Path("data/silver/reddit/cleaned_reddit_dataset.csv")
    # OUTPUT: Save to master dataset in consolidation folder
    output_csv_path = Path("data/silver/consolidation/master_dataset.csv")
    checkpoint_path = Path("data/silver/consolidation/sentiment_checkpoint.json")
    model_path = Path("Finetuning/output/models/best_model")

    # Check input file exists
    if not input_csv_path.exists():
        logger.error(f"Input CSV not found: {input_csv_path}")
        return {"status": "failed", "reason": "Input CSV not found"}

    if not model_path.exists():
        logger.error(f"Model not found: {model_path}")
        return {"status": "failed", "reason": "Model not found"}

    # 1. Load INPUT CSV (cleaned Reddit dataset)
    logger.info(f"Loading INPUT CSV: {input_csv_path}")
    df = pd.read_csv(input_csv_path)
    logger.info(f"Loaded {len(df)} rows from cleaned Reddit dataset")

    # 2. Load checkpoint
    processed_ids = set()
    if checkpoint_path.exists():
        logger.info("Loading checkpoint...")
        with open(checkpoint_path, 'r') as f:
            checkpoint = json.load(f)
            processed_ids = set(checkpoint.get('processed_ids', []))
        logger.info(f"Found {len(processed_ids)} already processed IDs")

    # 3. Check if sentiment column exists
    if 'sentiment' not in df.columns:
        logger.info("❌ 'sentiment' column NOT found - analyzing ALL rows")
        df['sentiment'] = None
        df['sentiment_confidence'] = None
        rows_to_process = df.copy()
    else:
        logger.info("✅ 'sentiment' column exists - analyzing NEW rows only")
        # Find rows without sentiment or not in checkpoint
        mask = (df['sentiment'].isna()) | (~df['unified_id'].isin(processed_ids))
        rows_to_process = df[mask].copy()
        logger.info(f"Found {len(rows_to_process)} new rows to process")

    if len(rows_to_process) == 0:
        logger.info("✅ No new rows to process - all up to date!")
        return {
            "status": "success",
            "total_rows": len(df),
            "processed_rows": 0,
            "already_processed": len(processed_ids)
        }

    # 4. Load model (lazy imports here)
    logger.info("Loading sentiment model...")

    try:
        # Import heavy libraries only when needed
        import torch
        from transformers import RobertaForSequenceClassification, RobertaTokenizer

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")

        tokenizer = RobertaTokenizer.from_pretrained(str(model_path))
        model = RobertaForSequenceClassification.from_pretrained(str(model_path))
        model.to(device)
        model.eval()
        logger.info("✅ Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return {"status": "failed", "reason": f"Model loading error: {e}"}

    # 5. Analyze sentiment
    logger.info(f"Analyzing sentiment for {len(rows_to_process)} rows...")
    texts = rows_to_process['text_content'].fillna("").astype(str).tolist()

    try:
        sentiments, confidences = analyze_sentiment_batch(
            texts, model, tokenizer, device, batch_size=32
        )

        # Update dataframe
        df.loc[rows_to_process.index, 'sentiment'] = sentiments
        df.loc[rows_to_process.index, 'sentiment_confidence'] = confidences

        logger.info("✅ Sentiment analysis completed")

    except Exception as e:
        logger.error(f"Error during sentiment analysis: {e}")
        return {"status": "failed", "reason": f"Analysis error: {e}"}

    # 6. Save updated CSV to master_dataset.csv (OUTPUT)
    logger.info(f"Saving updated CSV to OUTPUT: {output_csv_path}")
    # Ensure directory exists before saving
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    # If master_dataset.csv already exists, merge with existing data
    if output_csv_path.exists():
        logger.info(f"Master dataset exists - merging with existing data...")
        existing_df = pd.read_csv(output_csv_path)
        
        # Merge: Update existing rows or append new ones
        # Use unified_id as key for merging
        if 'unified_id' in existing_df.columns and 'unified_id' in df.columns:
            # Create a mapping of unified_id to sentiment from new analysis (faster than iterating)
            sentiment_updates = df.set_index('unified_id')[['sentiment', 'sentiment_confidence']]
            
            # Update existing dataframe with new sentiment values using merge
            existing_df = existing_df.set_index('unified_id')
            existing_df.update(sentiment_updates)
            existing_df = existing_df.reset_index()
            
            # Find new rows (not in existing dataset)
            existing_ids = set(existing_df['unified_id'])
            new_rows = df[~df['unified_id'].isin(existing_ids)]
            
            if len(new_rows) > 0:
                logger.info(f"Adding {len(new_rows)} new rows to master dataset")
                existing_df = pd.concat([existing_df, new_rows], ignore_index=True)
            
            df = existing_df
            logger.info(f"Merged with existing master dataset: {len(df)} total rows")
        else:
            # If no unified_id, just append and deduplicate
            df = pd.concat([existing_df, df], ignore_index=True)
            if 'unified_id' in df.columns:
                df = df.drop_duplicates(subset=['unified_id'], keep='last')
            logger.info(f"Appended to existing master dataset: {len(df)} total rows")
    else:
        logger.info("Master dataset does not exist - creating new file")
    
    df.to_csv(output_csv_path, index=False)
    logger.info(f"✅ CSV saved to OUTPUT: {output_csv_path}")

    # 7. Update checkpoint
    processed_ids.update(df['unified_id'].dropna().tolist())
    checkpoint = {
        'processed_ids': list(processed_ids),
        'last_updated': pd.Timestamp.now().isoformat(),
        'total_processed': len(processed_ids)
    }

    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    logger.info(f"✅ Checkpoint saved: {len(processed_ids)} total IDs")

    # 8. Summary
    result = {
        "status": "success",
        "total_rows": len(df),
        "processed_rows": len(rows_to_process),
        "sentiment_distribution": df['sentiment'].value_counts().to_dict(),
        "avg_confidence": df['sentiment_confidence'].mean()
    }

    logger.info("=" * 60)
    logger.info("SENTIMENT ANALYSIS COMPLETE")
    logger.info(f"Total rows: {result['total_rows']}")
    logger.info(f"Newly processed: {result['processed_rows']}")
    logger.info(f"Distribution: {result['sentiment_distribution']}")
    logger.info(f"Avg confidence: {result['avg_confidence']:.2%}")
    logger.info("=" * 60)

    return result
