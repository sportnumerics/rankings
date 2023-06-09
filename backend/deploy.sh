#!/usr/bin/env bash

environment=${1:-dev}

terraform -chdir=infra/environments/$environment init -input=false

terraform -chdir=infra/environments/$environment apply -input=false -auto-approve