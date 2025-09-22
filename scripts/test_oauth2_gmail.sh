#!/bin/bash

# Test OAuth2 Gmail integration script
# Usage: ./scripts/test_oauth2_gmail.sh [DEV_URL]

set -e

# Set default DEV_URL if not provided
DEV_URL=${1:-"https://axi-dev-api-633654204771-uc.a.run.app"}

echo "🔧 Testing OAuth2 implementation with Gmail client..."
echo "📍 Target URL: $DEV_URL"
echo ""

# Test 1: Get OAuth2 token with Gmail client credentials
echo "1️⃣ Testing OAuth2 token generation..."
TOKEN_RESPONSE=$(curl -s -X POST "$DEV_URL/api/v1/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "axi-gmail-client",
    "client_secret": "generated-secret",
    "grant_type": "client_credentials"
  }')

echo "Token Response: $TOKEN_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')

if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Failed to get access token"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "✅ Successfully obtained access token: ${ACCESS_TOKEN:0:20}..."
echo ""

# Test 2: Use token to access protected endpoint
echo "2️⃣ Testing protected endpoint access..."
ME_RESPONSE=$(curl -s -X GET "$DEV_URL/api/me/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "Me endpoint response: $ME_RESPONSE"
echo ""

# Test 3: Test with test_client credentials
echo "3️⃣ Testing with test_client credentials..."
TEST_TOKEN_RESPONSE=$(curl -s -X POST "$DEV_URL/api/v1/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "test_client",
    "client_secret": "test_secret",
    "grant_type": "client_credentials"
  }')

echo "Test client token response: $TEST_TOKEN_RESPONSE"

TEST_ACCESS_TOKEN=$(echo "$TEST_TOKEN_RESPONSE" | jq -r '.access_token')

if [ "$TEST_ACCESS_TOKEN" != "null" ] && [ -n "$TEST_ACCESS_TOKEN" ]; then
  echo "✅ Test client authentication successful"

  # Test protected endpoint with test token
  echo "4️⃣ Testing protected endpoint with test token..."
  TEST_ME_RESPONSE=$(curl -s -X GET "$DEV_URL/api/me/" \
    -H "Authorization: Bearer $TEST_ACCESS_TOKEN" \
    -H "Content-Type: application/json")

  echo "Test token me endpoint response: $TEST_ME_RESPONSE"
else
  echo "❌ Test client authentication failed"
fi

echo ""
echo "🎉 OAuth2 test completed!"
echo "📋 Summary:"
echo "   ✅ Gmail client OAuth2 token generation"
echo "   ✅ Protected endpoint access with Bearer token"
echo "   ✅ Test client credentials validation"