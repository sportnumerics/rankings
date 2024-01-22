#!/usr/bin/env bash

set -e

environment=${1:-dev}

npm run build

cp run.sh .next/standalone

terraform -chdir=infra/environments/$environment init -input=false

terraform -chdir=infra/environments/$environment apply -input=false -auto-approve
