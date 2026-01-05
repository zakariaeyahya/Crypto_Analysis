#!/bin/bash
# Test du découpage en chunks

echo "=========================================="
echo "  TEST CHUNKER"
echo "=========================================="

cd "$(dirname "$0")/../.."

# Activer l'environnement virtuel si existe
if [ -d "venv" ]; then
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
fi

# Fix Unicode pour Windows
export PYTHONIOENCODING=utf-8

# Exécuter le test
python tests/rag/test_chunker.py 2>/dev/null

exit $?
