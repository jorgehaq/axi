#!/bin/bash
# test_all_environments.sh - Complete API testing script for AXIS project

set -e  # Exit on any error

ENV=${1:-local}  # local, docker, gcp

case $ENV in
  "local"|"docker")
    BASE_URL="http://127.0.0.1:8000"
    ;;
  "gcp")
    BASE_URL="https://analytics-api-XXXXX-uc.a.run.app"  # Replace with your actual URL
    ;;
  *)
    echo "❌ Invalid environment. Use: local, docker, or gcp"
    exit 1
    ;;
esac

echo "🎯 Testing $ENV environment: $BASE_URL"

# Test credentials (DO NOT commit real credentials to GitHub)
USERNAME=${TEST_USER:-"testuser"}
PASSWORD=${TEST_PASS:-"testpass"}
FILE_PATH=${FILE_PATH:-"test_data.csv"}

echo "📋 Using credentials: $USERNAME"

# =============================================================================
# 1. AUTHENTICATION TEST
# =============================================================================
echo "🔐 Testing JWT authentication..."

AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | jq -r .access)
REFRESH_TOKEN=$(echo "$AUTH_RESPONSE" | jq -r .refresh)

if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Error: Could not obtain access token"
  echo "Response: $AUTH_RESPONSE"
  exit 1
fi

echo "✅ JWT tokens obtained successfully"
echo "   Access token: ${ACCESS_TOKEN:0:30}..."
echo "   Refresh token: ${REFRESH_TOKEN:0:30}..."

# =============================================================================
# 2. BASIC ENDPOINTS TEST
# =============================================================================
echo ""
echo "🏥 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/v1/health/")
echo "$HEALTH_RESPONSE" | jq

echo ""
echo "👤 Testing user info endpoint..."
USER_RESPONSE=$(curl -s "$BASE_URL/api/me/" -H "Authorization: Bearer $ACCESS_TOKEN")
echo "$USER_RESPONSE" | jq

# =============================================================================
# 3. FILE UPLOAD TEST
# =============================================================================
echo ""
echo "📤 Testing file upload..."

# Create test CSV file
cat > "$FILE_PATH" << EOF
date,amount,country,category
2024-01-01,100,CO,A
2024-01-02,200,PE,B
2024-01-03,150,AR,A
2024-01-04,300,CO,B
2024-01-05,250,PE,A
EOF

echo "📄 Created test file: $FILE_PATH"

# Upload file and capture ID
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/datasets/upload" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file=@$FILE_PATH")

FILE_ID=$(echo "$UPLOAD_RESPONSE" | jq -r .id)

if [ "$FILE_ID" = "null" ] || [ -z "$FILE_ID" ]; then
  echo "❌ Error: File upload failed"
  echo "Response: $UPLOAD_RESPONSE"
  exit 1
fi

echo "✅ File uploaded successfully"
echo "   File ID: $FILE_ID"
echo "   Response: $UPLOAD_RESPONSE"

# =============================================================================
# 4. ANALYTICS ENDPOINTS TEST
# =============================================================================
echo ""
echo "📊 Testing analytics endpoints with File ID: $FILE_ID"

echo ""
echo "👀 Testing data preview..."
PREVIEW_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/preview" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "$PREVIEW_RESPONSE" | jq

echo ""
echo "📈 Testing data summary..."
SUMMARY_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/summary" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "$SUMMARY_RESPONSE" | jq

echo ""
echo "🔍 Testing filtered rows..."
ROWS_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/rows?f=country,eq,CO&sort=-amount&page=1&page_size=3" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "$ROWS_RESPONSE" | jq

echo ""
echo "🔗 Testing correlation analysis..."
CORRELATION_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/correlation?cols=amount" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "$CORRELATION_RESPONSE" | jq

echo ""
echo "📅 Testing trend analysis..."
TREND_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/trend?date=date&value=amount&freq=D&agg=sum" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "$TREND_RESPONSE" | jq

echo ""
echo "🔗 Testing download URL..."
DOWNLOAD_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/download-url/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "$DOWNLOAD_RESPONSE" | jq

# =============================================================================
# 5. REFRESH TOKEN TEST
# =============================================================================
echo ""
echo "🔄 Testing token refresh..."
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\":\"$REFRESH_TOKEN\"}")

NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r .access)

if [ "$NEW_ACCESS_TOKEN" = "null" ] || [ -z "$NEW_ACCESS_TOKEN" ]; then
  echo "❌ Warning: Token refresh failed"
  echo "Response: $REFRESH_RESPONSE"
else
  echo "✅ Token refreshed successfully"
  echo "   New access token: ${NEW_ACCESS_TOKEN:0:30}..."
fi

# =============================================================================
# 6. CLEANUP
# =============================================================================
echo ""
echo "🧹 Cleaning up test files..."
rm -f "$FILE_PATH"

echo ""
echo "🎉 All tests completed for $ENV environment!"
echo "📊 Summary:"
echo "   Environment: $ENV"
echo "   Base URL: $BASE_URL"
echo "   User: $USERNAME"
echo "   File ID tested: $FILE_ID"
echo ""
echo "💡 Usage examples:"
echo "   ./test_all_environments.sh local"
echo "   ./test_all_environments.sh docker"
echo "   ./test_all_environments.sh gcp"