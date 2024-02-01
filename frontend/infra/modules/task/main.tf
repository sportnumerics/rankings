locals {
  bucket_name                             = "${var.data_bucket_prefix}-${var.environment}"
  lambda_origin                           = "lambda-origin"
  s3_bucket_origin                        = "s3-bucket-origin"
  aws_managed_caching_optimized_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"
}

data "archive_file" "package" {
  type        = "zip"
  source_dir  = "${path.cwd}/.next/standalone"
  output_path = "${path.cwd}/out/deployment.zip"
}

resource "aws_lambda_function" "lambda" {
  filename         = data.archive_file.package.output_path
  function_name    = "sportnumerics-ranking-frontend-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "run.sh"
  runtime          = "nodejs20.x"
  architectures    = ["x86_64"]
  layers           = ["arn:aws:lambda:${data.aws_region.current.name}:753240598075:layer:LambdaAdapterLayerX86:18"]
  memory_size      = 1024
  timeout          = 30
  source_code_hash = data.archive_file.package.output_base64sha256
  environment {
    variables = {
      "AWS_LAMBDA_EXEC_WRAPPER" = "/opt/bootstrap",
      "AWS_LWA_INVOKE_MODE"     = "response_stream",
      "PORT"                    = "8000"
      "NODE_ENV"                = "production"
      "DATA_BUCKET"             = local.bucket_name
    }
  }
}

resource "aws_lambda_function_url" "lambda" {
  function_name      = aws_lambda_function.lambda.function_name
  authorization_type = "NONE"
  invoke_mode        = "RESPONSE_STREAM"
}

resource "aws_iam_role" "lambda_role" {
  name               = "rankings-frontend-lambda-role-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = [
    aws_iam_policy.lambda_role.arn,
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]

  tags = {
    App   = "rankings"
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
    App   = "rankings"
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

module "static_files" {
  source = "hashicorp/dir/template"

  base_dir = "${path.cwd}/.next/static"
}

resource "aws_s3_object" "static_files" {
  for_each = module.static_files.files

  bucket       = local.bucket_name
  key          = "_next/static/${each.key}"
  content_type = each.value.content_type

  source  = each.value.source_path
  content = each.value.content

  etag = each.value.digests.md5
}

resource "aws_cloudfront_distribution" "frontend" {
  origin {
    origin_id   = local.lambda_origin
    domain_name = split("/", aws_lambda_function_url.lambda.function_url)[2]

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["SSLv3", "TLSv1.2"]
    }
  }

  origin {
    origin_id                = local.s3_bucket_origin
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
    domain_name              = "${local.bucket_name}.${var.website_domain}"
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US"]
    }
  }

  default_cache_behavior {
    allowed_methods  = ["HEAD", "OPTIONS", "GET"]
    cached_methods   = ["HEAD", "GET"]
    target_origin_id = local.lambda_origin

    cache_policy_id = aws_cloudfront_cache_policy.lambda_cache_policy.id

    viewer_protocol_policy = "redirect-to-https"
  }

  ordered_cache_behavior {
    path_pattern     = "_next/*"
    allowed_methods  = ["HEAD", "OPTIONS", "GET"]
    cached_methods   = ["HEAD", "GET"]
    target_origin_id = local.s3_bucket_origin

    cache_policy_id = local.aws_managed_caching_optimized_policy_id

    viewer_protocol_policy = "redirect-to-https"
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  enabled = true

  tags = {
    App   = "rankings"
    Stage = var.environment
  }
}

resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = "sportnumerics-rankings-frontend-${var.environment}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_s3_bucket_policy" "cloudfront_bucket_policy" {
  bucket = local.bucket_name
  policy = data.aws_iam_policy_document.cloudfront_bucket_policy.json
}

data "aws_iam_policy_document" "cloudfront_bucket_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = ["s3:GetObject"]

    resources = [
      "arn:aws:s3:::${local.bucket_name}/*"
    ]
  }
}

resource "aws_cloudfront_cache_policy" "lambda_cache_policy" {
  name = "lambda-cache-policy"

  min_ttl     = 1
  default_ttl = 600
  max_ttl     = 86400

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }

    headers_config {
      header_behavior = "whitelist"
      headers {
        items = ["Accept-Encoding"]
      }
    }

    query_strings_config {
      query_string_behavior = "all"
    }
  }
}
