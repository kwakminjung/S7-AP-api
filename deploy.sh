#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
  echo "Usage: ./deploy.sh v2.29"
  exit 1
fi

echo "== Delete Deployment =="
kubectl delete deployment --all -n netai

IMAGE_APLIST="kwakminjung/aplist_api:$VERSION"
IMAGE_TEMPLATE="kwakminjung/template_api:$VERSION"

echo "=== Building images ==="
docker build -t $IMAGE_APLIST .
docker build -t $IMAGE_TEMPLATE .

echo "=== Pushing images ==="
docker push $IMAGE_APLIST
docker push $IMAGE_TEMPLATE

echo "=== Helm upgrade ==="
helm upgrade s7-ap-api-release ./helm/s7-ap-api -n netai \
  --set aplistApi.image=$IMAGE_APLIST \
  --set templateApi.image=$IMAGE_TEMPLATE

echo "=== Done: $VERSION ==="

# ./deploy.sh v-.-