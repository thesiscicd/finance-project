#!/bin/bash

DOCKER_USERNAME=$1
DOCKER_PASSWORD=$2

# Log in to Docker Hub
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

# Stop and remove any existing Django containers
docker stop django-finance || true
docker rm django-finance || true

# Pull the latest Docker image
docker pull $DOCKER_USERNAME/django-finance:latest

# Run a new container
docker run -d --name django-finance -p 8000:8000 $DOCKER_USERNAME/django-finance:latest
