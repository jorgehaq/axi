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