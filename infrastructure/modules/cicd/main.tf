locals {
  oidc_provider_arn = "arn:aws:iam::265978616089:oidc-provider/token.actions.githubusercontent.com"
}

resource "aws_iam_role" "deployment_role" {
  name = "rankings-deployment-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Federated = local.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals : {
            "token.actions.githubusercontent.com:aud" : "sts.amazonaws.com"
            "token.actions.githubusercontent.com:sub" : "repo:sportnumerics/rankings:environment:production"
          }
        }
      }
    ]
  })
  managed_policy_arns = [
    aws_iam_policy.deployment_role.arn
  ]

  tags = {
    App = "rankings"
  }
}


resource "aws_iam_policy" "deployment_role" {
  name = "rankings-deployment-role-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:*",
          "ecr:*",
          "s3:*",
          "events:*",
          "logs:*",
          "ecr:*"
        ]
        Resource = [
          "*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "iam:CreateRole",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy"
        ],
        Resource = [
          "arn:aws:iam::265978616089:role/rankings-*"
        ],
        Condition = {
          StringEquals = {
            "iam:PermissionsBoundary" = aws_iam_policy.permissions_boundary.arn
          }
        }
      },
      {
        Effect = "Allow",
        Action = [
          "iam:TagRole",
          "iam:GetRole",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:ListInstanceProfilesForRole",
          "iam:DeleteRole"
        ],
        Resource = [
          "arn:aws:iam::265978616089:role/rankings-*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "iam:CreatePolicy",
          "iam:DeletePolicy",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:ListPolicyVersions",
          "iam:TagPolicy"
        ],
        Resource = [
          "arn:aws:iam::265978616089:policy/rankings-*"
        ]
      }
    ]
  })

  tags = {
    App = "rankings"
  }
}

resource "aws_iam_policy" "permissions_boundary" {
  name = "rankings-permissions-boundary"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          # AWSLambdaBasicExecutionRole
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",

          # AmazonECSTaskExecutionRolePolicy
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "logs:CreateLogStream",
          "logs:PutLogEvents",

          # backend rankings_backend_task_role
          "s3:DeleteObject",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject",

          # backend rankings_backend_scheduler_role
          "ecs:RunTask",
          "iam:PassRole",

          # frontend lambda_role
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Resource = [
          "*"
        ]
      }
    ]
  })

  tags = {
    App = "rankings"
  }
}
