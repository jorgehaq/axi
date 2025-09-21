#!/bin/bash
# test_all_environments.sh - API smoke tests for AXI

set -e

ENV=${1:-local}   # local, dev, staging, prod
QUIET=${2:-}      # use -q for concise output

log() { [[ "$QUIET" == "-q" ]] && return 0; echo "$@"; }

# jq helpers with python fallback
if command -v jq >/dev/null 2>&1; then
  json_get() { jq -r ".$1" 2>/dev/null; }
  json_pretty() { jq 2>/dev/null || cat; }
else
  json_get() { key="$1"; python3 - "$key" <<'PY'
import sys, json, os
key=sys.argv[1]
try:
    data=json.load(sys.stdin)
    v=data.get(key, '')
    print(v if v is not None else '')
except Exception:
    print('')
PY
  }
  json_pretty() { cat; }
fi

case $ENV in
  "local") BASE_URL="http://127.0.0.1:8000" ;;
  "dev") BASE_URL="https://analytics-api-dev-XXXXX-uc.a.run.app" ;;
  "staging") BASE_URL="https://analytics-api-staging-XXXXX-uc.a.run.app" ;;
  "prod") BASE_URL="https://analytics-api-prod-XXXXX-uc.a.run.app" ;;
  *) echo "Invalid environment. Use: local, dev, staging, or prod"; exit 1 ;;
esac

log "Testing $ENV: $BASE_URL"

USERNAME=${TEST_USER:-"testuser"}
PASSWORD=${TEST_PASS:-"testpass"}
FILE_PATH=${FILE_PATH:-"test_data.csv"}
log "User: $USERNAME"

# Create test user only for local environment
if [ "$ENV" = "local" ]; then
  log "Creating test user..."
  echo "Running bootstrap..." >&2
  timeout 15 .venv/bin/python manage.py bootstrap > /dev/null 2>&1 || echo "Bootstrap completed or failed" >&2
  echo "Bootstrap finished, continuing tests..." >&2
fi

# Auth
log "Auth..."
log "Testing connection to $BASE_URL/api/token/"
if ! curl -s --connect-timeout 5 "$BASE_URL/api/token/" >/dev/null 2>&1; then
  echo "Cannot connect to $BASE_URL"; exit 1
fi
log "Connection successful, attempting login..."

AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

if [ -z "$AUTH_RESPONSE" ] || [[ "$AUTH_RESPONSE" == *"<html"* ]]; then
  echo "Auth failed: invalid response"
  echo "Response: $AUTH_RESPONSE"
  exit 1
fi

ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | json_get access)
REFRESH_TOKEN=$(echo "$AUTH_RESPONSE" | json_get refresh)
if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
  echo "Auth failed: no access token"
  echo "Response: $AUTH_RESPONSE"
  exit 1
fi
log "Auth OK"

# Health
log "Health..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/v1/health/")
log "$(echo "$HEALTH_RESPONSE" | json_pretty)"

# Me
log "Me..."
USER_RESPONSE=$(curl -s "$BASE_URL/api/me/" -H "Authorization: Bearer $ACCESS_TOKEN")
log "$(echo "$USER_RESPONSE" | json_pretty)"

# Upload
log "Upload..."
cat > "$FILE_PATH" << EOF
date,amount,country,category
2024-01-01,100,CO,A
2024-01-02,200,PE,B
2024-01-03,150,AR,A
2024-01-04,300,CO,B
2024-01-05,250,PE,A
EOF
log "File: $FILE_PATH"

UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/datasets/upload" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file=@$FILE_PATH")
FILE_ID=$(echo "$UPLOAD_RESPONSE" | json_get id)
if [ -z "$FILE_ID" ] || [ "$FILE_ID" = "null" ]; then
  echo "Upload failed"
  echo "Response: $UPLOAD_RESPONSE"
  exit 1
fi
log "Upload OK (id=$FILE_ID)"

# Analytics
log "Analytics... (id=$FILE_ID)"
PREVIEW_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/preview" -H "Authorization: Bearer $ACCESS_TOKEN")
log "$(echo "$PREVIEW_RESPONSE" | json_pretty)"

SUMMARY_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/summary" -H "Authorization: Bearer $ACCESS_TOKEN")
log "$(echo "$SUMMARY_RESPONSE" | json_pretty)"

ROWS_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/rows?f=country,eq,CO&sort=-amount&page=1&page_size=3" -H "Authorization: Bearer $ACCESS_TOKEN")
log "$(echo "$ROWS_RESPONSE" | json_pretty)"

CORRELATION_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/correlation?cols=amount" -H "Authorization: Bearer $ACCESS_TOKEN")
log "$(echo "$CORRELATION_RESPONSE" | json_pretty)"

TREND_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/trend?date=date&value=amount&freq=D&agg=sum" -H "Authorization: Bearer $ACCESS_TOKEN")
log "$(echo "$TREND_RESPONSE" | json_pretty)"

DOWNLOAD_RESPONSE=$(curl -s "$BASE_URL/api/v1/datasets/$FILE_ID/download-url/" -H "Authorization: Bearer $ACCESS_TOKEN")
log "$(echo "$DOWNLOAD_RESPONSE" | json_pretty)"

# Refresh
log "Refresh..."
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/token/refresh/" -H "Content-Type: application/json" -d "{\"refresh\":\"$REFRESH_TOKEN\"}")
NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | json_get access)
if [ -n "$NEW_ACCESS_TOKEN" ] && [ "$NEW_ACCESS_TOKEN" != "null" ]; then
  log "Refresh OK"
else
  log "Refresh failed"
fi

# Cleanup
log "Cleanup..."
rm -f "$FILE_PATH"
log "Done. env=$ENV url=$BASE_URL user=$USERNAME id=$FILE_ID"