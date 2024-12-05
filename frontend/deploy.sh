#!/usr/bin/env bash

set -e

environment=${1:-dev}

npm install

npm run build

cp run.sh .next/standalone

terraform -chdir=infra/environments/$environment init -input=false

terraform -chdir=infra/environments/$environment apply -input=false -auto-approve

distribution_id=$(terraform -chdir=infra/environments/$environment output -raw cloudfront_distribution_id)

aws cloudfront create-invalidation \
    --distribution-id $distribution_id \
    --paths "/*"