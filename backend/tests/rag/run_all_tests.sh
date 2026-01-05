#!/bin/bash
# Exécute tous les tests RAG

echo "=========================================="
echo "  TESTS RAG - SUITE COMPLETE"
echo "=========================================="
echo ""

cd "$(dirname "$0")/../.."

# Activer l'environnement virtuel si existe
if [ -d "venv" ]; then
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
fi

# Fix Unicode pour Windows
export PYTHONIOENCODING=utf-8

# Compteurs
passed=0
failed=0
total=0

# Fonction pour exécuter un test
run_test() {
    local name=$1
    local script=$2

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    python $script 2>/dev/null

    if [ $? -eq 0 ]; then
        ((passed++))
        echo "  ✓ $name PASSED"
    else
        ((failed++))
        echo "  ✗ $name FAILED"
    fi
    ((total++))
}

# Exécuter les tests dans l'ordre
run_test "Configuration" "tests/rag/test_config.py"
run_test "Document Loader" "tests/rag/test_document_loader.py"
run_test "Chunker" "tests/rag/test_chunker.py"
run_test "Embedding Service" "tests/rag/test_embedding.py"
run_test "Pinecone Service" "tests/rag/test_pinecone.py"
run_test "Retriever Service" "tests/rag/test_retriever.py"
run_test "LLM Service" "tests/rag/test_llm.py"
run_test "RAG Service" "tests/rag/test_rag_service.py"

# Résumé final
echo ""
echo "=========================================="
echo "  RESUME FINAL"
echo "=========================================="
echo ""
echo "  Tests passés: $passed / $total"
echo "  Tests échoués: $failed / $total"
echo ""

if [ $failed -eq 0 ]; then
    echo "  ✓ TOUS LES TESTS SONT PASSES!"
    exit 0
else
    echo "  ✗ CERTAINS TESTS ONT ECHOUE"
    exit 1
fi
