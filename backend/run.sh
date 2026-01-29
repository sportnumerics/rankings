#!/usr/bin/env bash

set -euo pipefail

environment=${1:-dev}
year=${2:-}

cluster="rankings-backend-${environment}"
prefix="rankings-backend-${environment}"
task_definition="$(aws ecs list-task-definitions --family-prefix $prefix --sort DESC --max-items 1 | jq -r '.taskDefinitionArns[0]')"

schedule_name="rankings-backend-${environment}"
network_json="$(aws scheduler get-schedule --name "$schedule_name" --query 'Target.EcsParameters.NetworkConfiguration.awsvpcConfiguration' --output json 2>/dev/null || echo '{}')"

subnet_list="$(echo "$network_json" | jq -r '.Subnets // [] | join(",")')"
assign_ip="$(echo "$network_json" | jq -r '.AssignPublicIp // "ENABLED"')"

if [ -z "$subnet_list" ]; then
  subnet_list="subnet-f728fa92,subnet-866f9ff1"
fi

awsvpc_config="awsvpcConfiguration={subnets=[$subnet_list],assignPublicIp=$assign_ip}"

if [ -n "$year" ]; then
  container_override='{"name":"rankings-backend", "environment":[{"name":"YEAR", "value":"'"$year"'"}]}'
else
  container_override=''
fi

aws ecs run-task \
  --task-definition "$task_definition" \
  --cluster "$cluster" \
  --launch-type FARGATE \
  --network-configuration "$awsvpc_config" \
  --overrides '{"containerOverrides":['"$container_override"']}'
