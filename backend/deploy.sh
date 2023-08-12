#!/usr/bin/env bash

environment=${1:-dev}

terraform -chdir=infra/environments/$environment init -input=false

terraform -chdir=infra/environments/$environment apply -input=false -auto-approve

repository=$(terraform -chdir=infra/environments/$environment output -raw rankings_backend_repository)
image_url=$(terraform -chdir=infra/environments/$environment output -raw rankings_backend_image_url)

echo "logging into $repository"
aws ecr get-login-password | docker login --username AWS --password-stdin $repository

docker build -t "$image_url" .

docker push "$image_url"