#!/usr/bin/env bash

if [ ! -z "$1" ]; then
  container_override='{"name":"rankings-backend", "environment":[{"name":"YEAR", "value":"'"$1"'"}]}'
else
  container_override=''
fi

aws ecs run-task \
  --task-definition arn:aws:ecs:us-west-2:265978616089:task-definition/rankings-backend-dev:3 \
  --cluster rankings-backend-dev \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-f728fa92,subnet-866f9ff1],assignPublicIp=ENABLED}" \
  --overrides '{"containerOverrides":['"$container_override"']}'