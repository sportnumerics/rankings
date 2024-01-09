#!/usr/bin/env bash

aws ecs run-task \
  --task-definition arn:aws:ecs:us-west-2:265978616089:task-definition/rankings-backend-dev:3 \
  --cluster rankings-backend-dev \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-f728fa92,subnet-866f9ff1],assignPublicIp=ENABLED}"
