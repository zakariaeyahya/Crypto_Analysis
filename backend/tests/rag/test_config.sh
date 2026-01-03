#!/bin/bash
# Test de la configuration RAG

echo "=========================================="
echo "  TEST CONFIGURATION RAG"
echo "=========================================="

cd "$(dirname "$0")/../.."

# Activer l'environnement virtuel si existe
if [ -d "venv" ]; then
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
fi

# Fix Unicode pour Windows
export PYTHONIOENCODING=utf-8

# Exécuter le test
python tests/rag/test_config.py 2>/dev/null

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "Configuration OK!"
else
    echo ""
    echo "Configuration INCOMPLETE!"
fi

exit $exit_code
