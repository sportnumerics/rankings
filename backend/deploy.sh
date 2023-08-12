#!/usr/bin/env bash

environment=${1:-dev}

terraform -chdir=infra/environments/$environment init -input=false

terraform -chdir=infra/environments/$environment apply -input=false -auto-approve

repository=$(terraform -chdir=infra/environments/$environment output -raw rankings_backend_repository)
repository_url=$(terraform -chdir=infra/environments/$environment output -raw rankings_backend_repository_url)

echo "logging into $repository"
aws ecr get-login-password | docker login --username AWS --password-stdin $repository