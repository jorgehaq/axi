#!/bin/bash
# Test against real GCP dev environment

set -e

SERVICE_URL=$(gcloud run services describe axi-dev-api --region=us-central1 --format='value(status.url)' 2>/dev/null || true)
if [[ -z "$SERVICE_URL" ]]; then
  echo "Cloud Run service axi-dev-api not found or gcloud not configured." >&2
  exit 1
fi

BASE_URL="$SERVICE_URL"
echo "Testing dev environment: $BASE_URL"

export TEST_USER="devuser"
export TEST_PASS="devpass"

bash scripts/test_all_environment.sh dev

