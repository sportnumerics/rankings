#!/usr/bin/env bash

set -e

environment=${1:-dev}

terraform -chdir=infra/environments/$environment init -input=false

terraform -chdir=infra/environments/$environment apply -input=false -auto-approve

repository=$(terraform -chdir=infra/environments/$environment output -raw rankings_backend_repository)
image_url=$(terraform -chdir=infra/environments/$environment output -raw rankings_backend_image_url)
cache_ref="${image_url%:*}:buildcache"

echo "logging into $repository"
aws ecr get-login-password | docker login --username AWS --password-stdin $repository

docker buildx build \
    --push \
    --platform linux/arm64,linux/amd64 \
    --tag "$image_url" \
    --cache-from "type=registry,ref=${cache_ref}" \
    --cache-to "type=registry,ref=${cache_ref},mode=max" \
    .
