locals {
  bucket_name = "${var.bucket_prefix}-${var.environment}"
  bucket_url  = "s3://${local.bucket_name}/data"
  image_url   = "${aws_ecr_repository.rankings_backend.repository_url}:${var.image_tag}"
}

resource "aws_ecs_task_definition" "rankings_backend" {
  family = "rankings-backend-${var.environment}"

  execution_role_arn = aws_iam_role.rankings_backend_execution_role.arn
  task_role_arn      = aws_iam_role.rankings_backend_task_role.arn

  container_definitions = jsonencode([
    {
      "name" : "rankings-backend",
      "image" : local.image_url,
      "command" : ["--bucket-url", local.bucket_url]
      "logConfiguration" : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-region" : data.aws_region.current.name,
          "awslogs-group" : aws_cloudwatch_log_group.rankings_backend.name,
          "awslogs-stream-prefix" : "rankings-backend"
        }
      }
    }
  ])

  cpu                      = 256
  memory                   = 512
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  tags = {
    App   = "rankings"
    Stage = var.environment
  }
}

resource "aws_scheduler_schedule" "rankings_backend" {
  name = "rankings-backend-${var.environment}"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "rate(12 hours)"

  target {
    arn      = aws_ecs_cluster.rankings_backend.arn
    role_arn = aws_iam_role.rankings_backend_scheduler_role.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.rankings_backend.arn
      launch_type         = "FARGATE"
      network_configuration {
        assign_public_ip = true
        subnets          = var.subnets
      }
    }
  }
}

resource "aws_cloudwatch_event_rule" "task_exit_rule" {
  event_pattern = jsonencode({
    source      = ["aws.ecs"]
    detail-type = ["ECS Task State Change"]
    detail = {
      desiredStatus = ["STOPPED"]
      lastStatus    = ["STOPPED"]
    }
  })
}

resource "aws_cloudwatch_event_target" "task_exit_target" {
  rule      = aws_cloudwatch_event_rule.task_exit_rule.name
  target_id = "stopped-tasks"
  arn       = aws_cloudwatch_log_group.rankings_backend.arn
}

resource "aws_cloudwatch_log_resource_policy" "task_exit_log_resource_policy" {
  policy_name     = "rankings-backend-${var.environment}-task-exit-log-resource-policy"
  policy_document = data.aws_iam_policy_document.task_exit_log_resource_policy.json
}

data "aws_iam_policy_document" "task_exit_log_resource_policy" {
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:PutLogEventsBatch"
    ]

    resources = [aws_cloudwatch_log_group.rankings_backend.arn]

    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com", "events.amazonaws.com"]
    }
  }
}

resource "aws_ecs_cluster" "rankings_backend" {
  name = "rankings-backend-${var.environment}"
}

resource "aws_cloudwatch_log_group" "rankings_backend" {
  name = "/rankings/${var.environment}/backend"

  tags = {
    App   = "rankings"
    Stage = var.environment
  }
}

resource "aws_ecr_repository" "rankings_backend" {
  name = "rankings-backend-${var.environment}"

  tags = {
    App   = "rankings"
    Stage = var.environment
  }
}

resource "aws_iam_role" "rankings_backend_execution_role" {
  name                = "rankings-backend-execution-role-${var.environment}"
  assume_role_policy  = data.aws_iam_policy_document.rankings_backend_tasks_assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"]

  tags = {
    App   = "rankings"
    Stage = var.environment
  }
}

resource "aws_iam_role" "rankings_backend_task_role" {
  name                = "rankings-backend-task-role-${var.environment}"
  assume_role_policy  = data.aws_iam_policy_document.rankings_backend_tasks_assume_role.json
  managed_policy_arns = [aws_iam_policy.rankings_backend_task_role.arn]

  tags = {
    App   = "rankings"
    Stage = var.environment
  }
}

data "aws_iam_policy_document" "rankings_backend_tasks_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "rankings_backend_task_role" {
  name = "rankings-backend-task-role-policy-${var.environment}"

  policy = data.aws_iam_policy_document.rankings_backend_task_role.json

  tags = {
    App   = "rankings"
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
  name                = "rankings-backend-scheduler-role-${var.environment}"
  assume_role_policy  = data.aws_iam_policy_document.rankings_backend_scheduler_assume_role.json
  managed_policy_arns = [aws_iam_policy.rankings_backend_scheduler_role.arn]

  tags = {
    App   = "rankings"
    Stage = var.environment
  }
}

data "aws_iam_policy_document" "rankings_backend_scheduler_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "rankings_backend_scheduler_role" {
  name = "rankings-backend-scheduler-role-policy-${var.environment}"

  policy = data.aws_iam_policy_document.rankings_backend_scheduler_role.json

  tags = {
    App   = "rankings"
    Stage = var.environment
  }
}

data "aws_iam_policy_document" "rankings_backend_scheduler_role" {
  statement {
    actions = ["ecs:RunTask"]

    resources = [aws_ecs_task_definition.rankings_backend.arn]
  }

  statement {
    actions = ["iam:PassRole"]

    resources = [
      aws_iam_role.rankings_backend_task_role.arn,
      aws_iam_role.rankings_backend_execution_role.arn
    ]
  }
}

data "aws_region" "current" {}
