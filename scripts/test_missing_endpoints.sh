#!/bin/bash
# test_missing_endpoints.sh - Test for missing endpoints from instructions.md

set -e

ENV=${1:-local}
QUIET=${2:-}

log() { [[ "$QUIET" == "-q" ]] && return 0; echo "$@"; }

case $ENV in
  "local") BASE_URL="http://127.0.0.1:8000" ;;
  "dev") BASE_URL="https://analytics-api-dev-XXXXX-uc.a.run.app" ;;
  "staging") BASE_URL="https://analytics-api-staging-XXXXX-uc.a.run.app" ;;
  "prod") BASE_URL="https://analytics-api-prod-XXXXX-uc.a.run.app" ;;
  *) echo "Invalid environment. Use: local, dev, staging, or prod"; exit 1 ;;
esac

log "🔍 Testing missing endpoints for portfolio compatibility ($ENV)"
log "📋 Target: $BASE_URL"

MISSING_COUNT=0
FOUND_COUNT=0

# Helper function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3

    log "🧪 Testing $method $endpoint - $description"

    case $method in
        "GET")
            response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" 2>/dev/null || echo "000")
            ;;
        "POST")
            response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL$endpoint" -H "Content-Type: application/json" -d '{}' 2>/dev/null || echo "000")
            ;;
        *)
            response="000"
            ;;
    esac

    if [ "$response" = "000" ]; then
        log "❌ MISSING: $method $endpoint (Connection failed)"
        MISSING_COUNT=$((MISSING_COUNT + 1))
        return 1
    elif [ "$response" = "404" ]; then
        log "❌ MISSING: $method $endpoint (404 Not Found)"
        MISSING_COUNT=$((MISSING_COUNT + 1))
        return 1
    else
        log "✅ FOUND: $method $endpoint (HTTP $response)"
        FOUND_COUNT=$((FOUND_COUNT + 1))
        return 0
    fi
}

log ""
log "🎯 Testing required endpoints for portfolio compatibility:"
log ""

# 1. OAuth2 endpoint
test_endpoint "POST" "/api/v1/oauth/token" "OAuth2 client_credentials"

# 2. Health integrations
test_endpoint "GET" "/api/v1/health/integrations" "Status NEXUS/AIDE/ECHO"

# 3. Webhook Nexus
test_endpoint "POST" "/api/v1/webhooks/nexus" "Callback desde NEXUS"

# 4. Dataset metrics
test_endpoint "GET" "/api/v1/datasets/1/metrics" "Stats para GRASP"

log ""
log "📊 SUMMARY:"
log "   ✅ Found endpoints: $FOUND_COUNT"
log "   ❌ Missing endpoints: $MISSING_COUNT"
log "   📈 Portfolio compatibility: $((FOUND_COUNT * 100 / 4))%"

if [ $MISSING_COUNT -eq 0 ]; then
    log ""
    log "🎉 All required endpoints are implemented!"
    log "✅ Portfolio compatibility: COMPLETE"
    exit 0
else
    log ""
    log "⚠️  Missing endpoints detected!"
    log ""
    log "📝 TO IMPLEMENT:"

    # Check specific missing endpoints and provide implementation guidance
    if ! test_endpoint "POST" "/api/v1/oauth/token" "OAuth2" >/dev/null 2>&1; then
        log "   1. OAuth2 Token endpoint:"
        log "      - Create: apps/auth/urls.py"
        log "      - Add: path('oauth/token', oauth_token_view, name='oauth_token')"
        log "      - Include in: axi/urls.py → path('api/v1/', include('apps.auth.urls'))"
    fi

    if ! test_endpoint "GET" "/api/v1/health/integrations" "Health" >/dev/null 2>&1; then
        log "   2. Health Integrations endpoint:"
        log "      - Add to: apps/datasets/urls.py"
        log "      - path('health/integrations', health_integrations, name='health_integrations')"
    fi

    if ! test_endpoint "POST" "/api/v1/webhooks/nexus" "Webhook" >/dev/null 2>&1; then
        log "   3. Nexus Webhook endpoint:"
        log "      - Add to: apps/datasets/urls.py"
        log "      - path('webhooks/nexus', nexus_webhook, name='nexus_webhook')"
    fi

    if ! test_endpoint "GET" "/api/v1/datasets/1/metrics" "Metrics" >/dev/null 2>&1; then
        log "   4. Dataset Metrics endpoint:"
        log "      - Add to: apps/datasets/urls.py"
        log "      - path('datasets/<int:id>/metrics', dataset_metrics, name='dataset_metrics')"
    fi

    log ""
    log "📚 Current status: AXI V1 has 80% functionality"
    log "🎯 Goal: Add these 4 endpoints for full portfolio compatibility"

    exit 1
fi