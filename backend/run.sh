#!/usr/bin/env bash

set -euo pipefail

environment=${1:-dev}
year=${2:-}
scrape_limit=${3:-${SCRAPE_LIMIT:-}}

cluster="rankings-backend-${environment}"
prefix="rankings-backend-${environment}"
task_definition="$(aws ecs list-task-definitions --family-prefix $prefix --sort DESC --max-items 1 | jq -r '.taskDefinitionArns[0]')"
if [ -z "$task_definition" ] || [ "$task_definition" = "null" ]; then
  echo "No ECS task definition found for family prefix: $prefix" >&2
  exit 1
fi

schedule_name="rankings-backend-${environment}"
network_json="$(aws scheduler get-schedule --name "$schedule_name" --query 'Target.EcsParameters.NetworkConfiguration.awsvpcConfiguration' --output json 2>/dev/null || echo '{}')"

subnet_list="$(echo "$network_json" | jq -r '.Subnets // [] | join(",")')"
assign_ip="$(echo "$network_json" | jq -r '.AssignPublicIp // "ENABLED"')"

if [ -z "$subnet_list" ]; then
  subnet_list="subnet-f728fa92,subnet-866f9ff1"
fi

awsvpc_config="awsvpcConfiguration={subnets=[$subnet_list],assignPublicIp=$assign_ip}"

env_overrides=()
if [ -n "$year" ]; then
  env_overrides+=("{\"name\":\"YEAR\",\"value\":\"$year\"}")
fi
if [ -n "$scrape_limit" ]; then
  env_overrides+=("{\"name\":\"SCRAPE_LIMIT\",\"value\":\"$scrape_limit\"}")
fi

container_overrides='[]'
if [ ${#env_overrides[@]} -gt 0 ]; then
  env_json="$(printf '%s\n' "${env_overrides[@]}" | jq -s '.')"
  container_overrides="$(jq -nc --argjson env "$env_json" '[{name:"rankings-backend", environment:$env}]')"
fi

aws ecs run-task \
  --task-definition "$task_definition" \
  --cluster "$cluster" \
  --launch-type FARGATE \
  --network-configuration "$awsvpc_config" \
  --overrides "$(jq -nc --argjson overrides "$container_overrides" '{containerOverrides: $overrides}')"
