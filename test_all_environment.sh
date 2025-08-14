#!/bin/bash
# test_all_environments.sh

ENV=${1:-local}  # local, docker, gcp

case $ENV in
  "local"|"docker")
    BASE_URL="http://127.0.0.1:8000"
    ;;
  "gcp")
    BASE_URL="https://analytics-api-XXXXX-uc.a.run.app"  # Cambiar por tu URL
    ;;
esac

echo "🎯 Testing $ENV environment: $BASE_URL"

# Token
ACCESS=$(curl -s -X POST $BASE_URL/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Pedazov5."}' | jq -r .access)

echo "✅ Token obtenido"

# Run all tests
curl -s $BASE_URL/api/health/ | jq
curl -s $BASE_URL/api/me/ -H "Authorization: Bearer $ACCESS" | jq

echo "🔥 Tests completados para $ENV"