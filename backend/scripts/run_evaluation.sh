#!/bin/bash
# ==============================================================================
# Script d'evaluation RAGAS pour le chatbot RAG Crypto
# ==============================================================================
#
# Usage:
#   ./scripts/run_evaluation.sh          # Evaluation rapide (5 samples)
#   ./scripts/run_evaluation.sh full     # Evaluation complete RAGAS
#   ./scripts/run_evaluation.sh stats    # Statistiques du dataset
#   ./scripts/run_evaluation.sh query "Quel est le sentiment de Bitcoin?"
#
# ==============================================================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repertoire du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}       RAGAS Evaluation - Crypto RAG        ${NC}"
echo -e "${BLUE}=============================================${NC}"

# Aller dans le repertoire backend
cd "$BACKEND_DIR"

# Verifier l'environnement Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}Python non trouve!${NC}"
    exit 1
fi

# Verifier le fichier .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Attention: .env non trouve${NC}"
fi

# Determiner le mode
MODE="${1:-quick}"

case "$MODE" in
    "quick")
        echo -e "\n${GREEN}Mode: Evaluation rapide (5 samples)${NC}\n"
        python scripts/evaluate_rag.py --quick
        ;;

    "full")
        echo -e "\n${GREEN}Mode: Evaluation complete RAGAS${NC}\n"
        python scripts/evaluate_rag.py --full --samples 20
        ;;

    "simple")
        echo -e "\n${GREEN}Mode: Evaluation simple (heuristiques)${NC}\n"
        python scripts/evaluate_rag.py --simple --samples 10
        ;;

    "stats")
        echo -e "\n${GREEN}Mode: Statistiques du dataset${NC}\n"
        python scripts/evaluate_rag.py --stats
        ;;

    "query")
        if [ -z "$2" ]; then
            echo -e "${RED}Erreur: Specifiez une question${NC}"
            echo "Usage: $0 query \"Votre question\""
            exit 1
        fi
        echo -e "\n${GREEN}Mode: Test question unique${NC}\n"
        python scripts/evaluate_rag.py --query "$2"
        ;;

    "category")
        if [ -z "$2" ]; then
            echo -e "${RED}Erreur: Specifiez une categorie${NC}"
            echo "Categories: sentiment_general, comparison, correlation, temporal, detailed, vague, faq"
            exit 1
        fi
        echo -e "\n${GREEN}Mode: Evaluation categorie '$2'${NC}\n"
        python scripts/evaluate_rag.py --category "$2" --samples 5
        ;;

    "help"|"-h"|"--help")
        echo ""
        echo "Usage: $0 [MODE] [OPTIONS]"
        echo ""
        echo "Modes disponibles:"
        echo "  quick      Evaluation rapide (5 samples, heuristiques) [defaut]"
        echo "  full       Evaluation complete avec RAGAS (20 samples)"
        echo "  simple     Evaluation heuristiques (10 samples)"
        echo "  stats      Afficher les statistiques du dataset"
        echo "  query      Tester une question: $0 query \"Question?\""
        echo "  category   Evaluer une categorie: $0 category comparison"
        echo "  help       Afficher cette aide"
        echo ""
        echo "Categories:"
        echo "  sentiment_general, comparison, correlation"
        echo "  temporal, detailed, vague, faq"
        echo ""
        ;;

    *)
        echo -e "${RED}Mode inconnu: $MODE${NC}"
        echo "Utilisez '$0 help' pour voir les options"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Done!${NC}"
