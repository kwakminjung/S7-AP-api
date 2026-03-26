#!/bin/bash

IMAGE_NAME="s7-ap-fastapi-app"
CONTAINER_NAME="s7-ap-fastapi-container"

docker build -t $IMAGE_NAME .

docker run -it --rm \
    -p 8000:8000 \
    -v $(pwd)/app/data:/workspace/app/data \
    --name $CONTAINER_NAME $IMAGE_NAME