#!/bin/bash
# Test de l'API Chat

echo "=========================================="
echo "  TEST API CHAT ENDPOINTS"
echo "=========================================="

cd "$(dirname "$0")/../.."

# Activer l'environnement virtuel si existe
if [ -d "venv" ]; then
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
fi

# Fix Unicode pour Windows
export PYTHONIOENCODING=utf-8

# Vérifier que le serveur est lancé
echo "Vérification du serveur..."
curl -s http://localhost:8000/docs > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo ""
    echo "ERREUR: Le serveur n'est pas lance!"
    echo ""
    echo "Lancez d'abord le serveur avec:"
    echo "  uvicorn app.main:app --reload --port 8000"
    echo ""
    exit 1
fi

# Exécuter le test
python tests/rag/test_api_chat.py 2>/dev/null

exit $?
