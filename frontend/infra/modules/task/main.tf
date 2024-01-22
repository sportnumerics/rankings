locals {
    bucket_name = "${var.data_bucket_prefix}-${var.environment}"
}

data "archive_file" "package" {
    type = "zip"
    source_dir = "${path.cwd}/.next/standalone"
    output_path = "${path.cwd}/out/deployment.zip"
}

resource "aws_lambda_function" "lambda" {
    filename = data.archive_file.package.output_path
    function_name = "sportnumerics-ranking-frontend-${var.environment}"
    role = aws_iam_role.lambda_role.arn
    handler = "run.sh"
    runtime = "nodejs20.x"
    architectures = [ "x86_64" ]
    layers = ["arn:aws:lambda:${data.aws_region.current.name}:753240598075:layer:LambdaAdapterLayerX86:18"]
    memory_size = 1024
    timeout = 30
    source_code_hash = data.archive_file.package.output_base64sha256
    environment {
        variables = {
            "AWS_LAMBDA_EXEC_WRAPPER" = "/opt/bootstrap",
            "PORT" = "8000"
            "NODE_ENV" = "production"
            "DATA_BUCKET" = local.bucket_name
        }
    }
}

resource "aws_lambda_function_url" "lambda" {
    function_name = aws_lambda_function.lambda.function_name
    authorization_type = "NONE"
}

resource "aws_iam_role" "lambda_role" {
    name = "rankings-frontend-lambda-role-${var.environment}"
    assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
    managed_policy_arns = [
        aws_iam_policy.lambda_role.arn,
        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    ]

    tags = {
        App = "rankings"
        Stage = var.environment
    }
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "lambda_role" {
    name = "rankings-frontend-lambda-role-policy-${var.environment}"

    policy = data.aws_iam_policy_document.lambda_role.json

    tags = {
        App = "rankings"
        Stage = var.environment
    }
}

data "aws_iam_policy_document" "lambda_role" {
    statement {
        actions = [
            "s3:GetObject",
            "s3:ListBucket"
        ]

        resources = [
            "arn:aws:s3:::${local.bucket_name}",
            "arn:aws:s3:::${local.bucket_name}/*"
        ]
    }
}


data "aws_region" "current" {}