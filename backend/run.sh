#!/usr/bin/env bash

environment=${1:-dev}

if [ ! -z "$2" ]; then
  container_override='{"name":"rankings-backend", "environment":[{"name":"YEAR", "value":"'"$2"'"}]}'
else
  container_override=''
fi

cluster="rankings-backend-${environment}"
prefix="rankings-backend-${environment}"
task_definition="$(aws ecs list-task-definitions --family-prefix $prefix | jq -r '.taskDefinitionArns[0]')"

aws ecs run-task \
  --task-definition $task_definition \
  --cluster $cluster \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-f728fa92,subnet-866f9ff1],assignPublicIp=ENABLED}" \
  --overrides '{"containerOverrides":['"$container_override"']}'