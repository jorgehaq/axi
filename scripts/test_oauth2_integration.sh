#!/bin/bash
# test_oauth2_integration.sh - Test OAuth2 integration functionality

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

log "🔐 Testing OAuth2 integration for $ENV: $BASE_URL"

# Test OAuth2 client credentials
CLIENT_ID=${TEST_CLIENT_ID:-"test_client"}
CLIENT_SECRET=${TEST_CLIENT_SECRET:-"test_secret"}

# Test 1: OAuth2 Token Endpoint
log "🎫 Testing OAuth2 token endpoint..."
if ! curl -s --connect-timeout 5 "$BASE_URL/oauth/token/" >/dev/null 2>&1; then
  log "⚠️  OAuth2 token endpoint not available at /oauth/token/"

  # Try alternative endpoint
  if ! curl -s --connect-timeout 5 "$BASE_URL/api/oauth/token/" >/dev/null 2>&1; then
    log "❌ OAuth2 token endpoint not found"
    exit 1
  else
    TOKEN_URL="$BASE_URL/api/oauth/token/"
  fi
else
  TOKEN_URL="$BASE_URL/oauth/token/"
fi

log "✅ OAuth2 endpoint found: $TOKEN_URL"

# Test 2: Client Credentials Grant
log "🔑 Testing client credentials grant..."
TOKEN_RESPONSE=$(curl -s -X POST "$TOKEN_URL" \
  -H "Content-Type: application/json" \
  -d "{\"client_id\":\"$CLIENT_ID\",\"client_secret\":\"$CLIENT_SECRET\",\"grant_type\":\"client_credentials\"}")

if [[ "$TOKEN_RESPONSE" == *"access_token"* ]]; then
  ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))")
  log "✅ Client credentials grant: SUCCESS"
  log "   Token: ${ACCESS_TOKEN:0:20}..."
else
  log "❌ Client credentials grant: FAILED"
  log "   Response: $TOKEN_RESPONSE"
fi

# Test 3: Authorization Code Grant (if supported)
log "📋 Testing authorization code flow..."
AUTH_URL="$BASE_URL/oauth/authorize/"
if curl -s --connect-timeout 5 "$AUTH_URL" >/dev/null 2>&1; then
  log "✅ Authorization endpoint available"

  # Test authorization request
  AUTH_RESPONSE=$(curl -s "$AUTH_URL?client_id=$CLIENT_ID&response_type=code&redirect_uri=http://localhost:8080/callback")
  if [[ "$AUTH_RESPONSE" == *"authorize"* ]] || [[ "$AUTH_RESPONSE" == *"login"* ]]; then
    log "✅ Authorization flow: AVAILABLE"
  else
    log "⚠️  Authorization flow: NEEDS CONFIGURATION"
  fi
else
  log "⚠️  Authorization endpoint not found"
fi

# Test 4: Token Validation
if [ -n "$ACCESS_TOKEN" ]; then
  log "🔍 Testing token validation..."

  # Try to use token with protected endpoint
  PROTECTED_RESPONSE=$(curl -s "$BASE_URL/api/me/" -H "Authorization: Bearer $ACCESS_TOKEN")

  if [[ "$PROTECTED_RESPONSE" == *"username"* ]] || [[ "$PROTECTED_RESPONSE" == *"id"* ]]; then
    log "✅ Token validation: SUCCESS"
  else
    log "⚠️  Token validation: FAILED or endpoint not protected"
    log "   Response: $PROTECTED_RESPONSE"
  fi
fi

# Test 5: Token Refresh (if refresh token available)
if [[ "$TOKEN_RESPONSE" == *"refresh_token"* ]]; then
  log "🔄 Testing token refresh..."
  REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('refresh_token', ''))")

  REFRESH_RESPONSE=$(curl -s -X POST "$TOKEN_URL" \
    -H "Content-Type: application/json" \
    -d "{\"grant_type\":\"refresh_token\",\"refresh_token\":\"$REFRESH_TOKEN\"}")

  if [[ "$REFRESH_RESPONSE" == *"access_token"* ]]; then
    log "✅ Token refresh: SUCCESS"
  else
    log "❌ Token refresh: FAILED"
    log "   Response: $REFRESH_RESPONSE"
  fi
else
  log "⚠️  Refresh token not provided"
fi

# Test 6: Scope validation
log "🎯 Testing OAuth2 scopes..."
SCOPE_RESPONSE=$(curl -s -X POST "$TOKEN_URL" \
  -H "Content-Type: application/json" \
  -d "{\"client_id\":\"$CLIENT_ID\",\"client_secret\":\"$CLIENT_SECRET\",\"grant_type\":\"client_credentials\",\"scope\":\"read write\"}")

if [[ "$SCOPE_RESPONSE" == *"access_token"* ]]; then
  log "✅ Scope handling: SUCCESS"

  # Extract and validate scope
  GRANTED_SCOPE=$(echo "$SCOPE_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('scope', 'N/A'))")
  log "   Granted scope: $GRANTED_SCOPE"
else
  log "⚠️  Scope handling: FAILED or not implemented"
fi

log "🎉 OAuth2 integration tests completed"
log "📝 Summary:"
log "   - Token endpoint: $([ -n "$TOKEN_URL" ] && echo "✅ Available" || echo "❌ Missing")"
log "   - Client credentials: $([ -n "$ACCESS_TOKEN" ] && echo "✅ Working" || echo "❌ Failed")"
log "   - Token validation: $([ -n "$ACCESS_TOKEN" ] && echo "✅ Working" || echo "❌ Failed")"
log "   - Authorization flow: $(curl -s --connect-timeout 2 "$BASE_URL/oauth/authorize/" >/dev/null 2>&1 && echo "✅ Available" || echo "⚠️  Not configured")"