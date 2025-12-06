#!/bin/bash
# Quick DAG validation script
# Run this before building Docker image

echo "=========================================="
echo "DAG VALIDATION BEFORE DOCKER BUILD"
echo "=========================================="

DAG_FILE="airflow/dags/complete_crypto_pipeline_unified.py"

# Check if file exists
if [ ! -f "$DAG_FILE" ]; then
    echo "ERROR: DAG file not found: $DAG_FILE"
    exit 1
fi

echo "✓ DAG file exists"

# Check Python syntax
echo "Checking Python syntax..."
python -m py_compile "$DAG_FILE" 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Python syntax is valid"
else
    echo "✗ Python syntax error!"
    exit 1
fi

# Check for required functions
echo "Checking function definitions..."
grep -q "def extract_reddit_data" "$DAG_FILE" && echo "✓ extract_reddit_data found" || echo "✗ extract_reddit_data missing"
grep -q "def clean_reddit_data" "$DAG_FILE" && echo "✓ clean_reddit_data found" || echo "✗ clean_reddit_data missing"
grep -q "def analyze_sentiment" "$DAG_FILE" && echo "✓ analyze_sentiment found" || echo "✗ analyze_sentiment missing"

# Check for task definitions
echo "Checking task definitions..."
grep -q "extract_task" "$DAG_FILE" && echo "✓ extract_task found" || echo "✗ extract_task missing"
grep -q "clean_task" "$DAG_FILE" && echo "✓ clean_task found" || echo "✗ clean_task missing"
grep -q "sentiment_task" "$DAG_FILE" && echo "✓ sentiment_task found" || echo "✗ sentiment_task missing"

# Check for dependencies
echo "Checking task dependencies..."
grep -q "extract_task >> clean_task" "$DAG_FILE" && echo "✓ Task dependencies found" || echo "⚠ Task dependencies might be missing"

echo ""
echo "=========================================="
echo "VALIDATION COMPLETE"
echo "=========================================="
echo ""
echo "If all checks passed, you can build Docker image:"
echo "  docker-compose build"
echo ""

