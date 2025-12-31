#!/bin/bash

# ============================================
# Test Script - Crypto Dashboard API
# ============================================

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================"
echo "  Testing Crypto Dashboard API"
echo "============================================"
echo ""

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    
    echo -n "Testing: $description... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    
    if [ "$response" == "200" ]; then
        echo -e "${GREEN}OK${NC} (HTTP $response)"
    else
        echo -e "${RED}FAILED${NC} (HTTP $response)"
    fi
}

# Health Check
echo "--- Health ---"
test_endpoint GET "/" "Root endpoint"
test_endpoint GET "/health" "Health check"
echo ""

# Cryptos
echo "--- Cryptos ---"
test_endpoint GET "/api/cryptos" "List all cryptos with prices"
test_endpoint GET "/api/cryptos/BTC" "Get Bitcoin"
test_endpoint GET "/api/cryptos/ETH" "Get Ethereum"
test_endpoint GET "/api/cryptos/SOL" "Get Solana"
test_endpoint GET "/api/cryptos/BTC/chart" "BTC price chart (7 days)"
test_endpoint GET "/api/cryptos/ETH/chart?days=30" "ETH price chart (30 days)"
echo ""

# Sentiment
echo "--- Sentiment ---"
test_endpoint GET "/api/sentiment/global" "Global sentiment"
test_endpoint GET "/api/sentiment/BTC/timeline" "BTC timeline"
test_endpoint GET "/api/sentiment/ETH/timeline?days=7" "ETH timeline (7 days)"
test_endpoint GET "/api/sentiment/SOL/timeline?days=30" "SOL timeline (30 days)"
echo ""

# Analysis
echo "--- Analysis ---"
test_endpoint GET "/api/analysis/BTC/correlation" "BTC correlation"
test_endpoint GET "/api/analysis/BTC/lag" "BTC lag analysis"
test_endpoint GET "/api/analysis/BTC/stats" "BTC full stats"
test_endpoint GET "/api/analysis/ETH/stats" "ETH full stats"
test_endpoint GET "/api/analysis/SOL/stats" "SOL full stats"
test_endpoint GET "/api/analysis/BTC/scatter" "BTC scatter data"
test_endpoint GET "/api/analysis/ETH/scatter?days=30" "ETH scatter (30 days)"
echo ""

# Events
echo "--- Events ---"
test_endpoint GET "/api/events" "All events"
test_endpoint GET "/api/events?crypto=BTC" "BTC events"
test_endpoint GET "/api/events?crypto=ETH&limit=10" "ETH events (limit 10)"
test_endpoint GET "/api/events/stats" "Events stats"
test_endpoint GET "/api/events/stats?crypto=BTC" "BTC events stats"
echo ""

echo "============================================"
echo "  Tests completed!"
echo "============================================"

# Show sample response
echo ""
echo "--- Sample Response: /api/sentiment/global ---"
curl -s "$BASE_URL/api/sentiment/global" | python -m json.tool 2>/dev/null || curl -s "$BASE_URL/api/sentiment/global"
echo ""
