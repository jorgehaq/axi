#!/bin/bash
set -e

# Variables
PROJECT_ID="analytics-api-portfolio"
REGION="us-central1"
REPO="analytics-repo"
SERVICE_NAME="analytics-api"

IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_NAME:$(git rev-parse --short HEAD)"

echo "Building and deploying: $IMAGE"

# Build, push, deploy
docker build -t $IMAGE .
docker push $IMAGE
gcloud run deploy $SERVICE_NAME --image $IMAGE --region $REGION --allow-unauthenticated

# Al final de deploy.sh, agregar:
echo "🔧 Running bootstrap command..."
gcloud run jobs create bootstrap-users \
  --image $IMAGE \
  --region $REGION \
  --add-cloudsql-instances $CONN_NAME \
  --set-env-vars DB_ENGINE=postgres,DB_NAME=analytics,DB_USER=analytics,DB_PASSWORD=$DB_PASSWORD,DB_HOST=/cloudsql/$CONN_NAME \
  --command python \
  --args "manage.py,bootstrap" \
  --execute-now \
  --wait

# Al final de deploy.sh, agregar:
echo "🔧 Running bootstrap command..."
gcloud run jobs create bootstrap-users \
  --image $IMAGE \
  --region $REGION \
  --add-cloudsql-instances $CONN_NAME \
  --set-env-vars DB_ENGINE=postgres,DB_NAME=analytics,DB_USER=analytics,DB_PASSWORD=$DB_PASSWORD,DB_HOST=/cloudsql/$CONN_NAME \
  --command python \
  --args "manage.py,bootstrap" \
  --execute-now \
  --wait

echo "✅ Bootstrap completed!"
