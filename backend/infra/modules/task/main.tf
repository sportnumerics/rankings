locals {
    bucket_name = "${var.bucket_prefix}-${var.environment}"
}

resource "aws_ecs_task_definition" "rankings_backend" {
    family = "rankings-backend-${var.environment}"

    execution_role_arn = aws_iam_role.rankings_backend_execution_role.arn
    task_role_arn = aws_iam_role.rankings_backend_task_role.arn

    container_definitions = jsonencode([
        {
            "name": "rankings-backend",
            "image": "${aws_ecr_repository.rankings_backend.repository_url}/backend:latest",
            "command": ["--bucket-url", "s3://${local.bucket_name}/data"]
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-region": data.aws_region.current.name,
                    "awslogs-group": aws_cloudwatch_log_group.rankings_backend.name,
                    "awslogs-stream-prefix": "rankings-backend"
                }
            }
        }
    ])

    cpu = 256
    memory = 512
    requires_compatibilities = ["FARGATE"]
    network_mode = "awsvpc"

    tags = {
        App = "rankings"
        Stage = var.environment
    }
}

resource "aws_scheduler_schedule" "rankings_backend" {
    name = "rankings-backend-${var.environment}"

    flexible_time_window {
      mode = "OFF"
    }

    schedule_expression = "rate(8 hours)"

    target {
        arn = aws_ecs_cluster.rankings_backend.arn
        role_arn = aws_iam_role.rankings_backend_scheduler_role.arn

        ecs_parameters {
          task_definition_arn = aws_ecs_task_definition.rankings_backend.arn
          launch_type = "FARGATE"
          network_configuration {
            assign_public_ip = true
            subnets = var.subnets
          }
        }
    }
}

resource "aws_ecs_cluster" "rankings_backend" {
    name = "rankings-backend-${var.environment}"
}

resource "aws_cloudwatch_log_group" "rankings_backend" {
  name = "/rankings/${var.environment}/backend"

  tags = {
        App = "rankings"
        Stage = var.environment
    }
}

resource "aws_ecr_repository" "rankings_backend" {
    name = "rankings-backend-${var.environment}"

    tags = {
        App = "rankings"
        Stage = var.environment
    }
}

resource "aws_iam_role" "rankings_backend_execution_role" {
    name = "rankings-backend-execution-role-${var.environment}"
    assume_role_policy = data.aws_iam_policy_document.rankings_backend_assume_role_policy.json

    tags = {
        App = "rankings"
        Stage = var.environment
    }
}

data "aws_iam_policy_document" "rankings_backend_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "rankings_backend_execution_role" {
    role = aws_iam_role.rankings_backend_execution_role.name
    policy_arn = data.aws_iam_policy.rankings_backend_execution_role.arn
}

data "aws_iam_policy" "rankings_backend_execution_role" {
    arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "rankings_backend_task_role" {
    name = "rankings-backend-task-role-${var.environment}"
    assume_role_policy = data.aws_iam_policy_document.rankings_backend_assume_role_policy.json

    inline_policy {
        policy = data.aws_iam_policy_document.rankings_backend_task_role.json
    }

    tags = {
        App = "rankings"
        Stage = var.environment
    }
}

data "aws_iam_policy_document" "rankings_backend_task_role" {
    statement {
        actions = [
            "s3:DeleteObject",
            "s3:GetBucketLocation",
            "s3:GetObject",
            "s3:ListBucket",
            "s3:PutObject"
        ]

        resources = [
            "arn:aws:s3:::${local.bucket_name}",
            "arn:aws:s3:::${local.bucket_name}/*"
        ]
    }
}

resource "aws_iam_role" "rankings_backend_scheduler_role" {
    name = "rankings-backend-scheduler-role-${var.environment}"
    assume_role_policy = data.aws_iam_policy_document.rankings_backend_scheduler_assume_role_policy.json

    inline_policy {
      policy = data.aws_iam_policy_document.rankings_backend_scheduler_role.json
    }

    tags = {
        App = "rankings"
        Stage = var.environment
    }
}

data "aws_iam_policy_document" "rankings_backend_scheduler_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "rankings_backend_scheduler_role" {
    statement {
        actions = ["ecs:RunTask"]

        resources = [aws_ecs_task_definition.rankings_backend.arn]
    }
}

data "aws_region" "current" {}