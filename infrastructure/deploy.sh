#!/usr/bin/env bash

environment=${1:-dev}

terraform -chdir=environments/$environment init -input=false

terraform -chdir=environments/$environment apply -input=false -auto-approve