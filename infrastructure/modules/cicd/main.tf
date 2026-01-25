locals {
  oidc_provider_arn = "arn:aws:iam::265978616089:oidc-provider/token.actions.githubusercontent.com"
  account_id        = "265978616089"
}

# =============================================================================
# PROD DEPLOYMENT ROLE - only main branch can assume
# =============================================================================
resource "aws_iam_role" "deployment_role_prod" {
  name = "rankings-deployment-role-prod"
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
            "token.actions.githubusercontent.com:sub" : "repo:sportnumerics/rankings:ref:refs/heads/main"
          }
        }
      }
    ]
  })
  managed_policy_arns = [
    aws_iam_policy.deployment_role_prod.arn
  ]

  tags = {
    App   = "rankings"
    Stage = "prod"
  }
}

resource "aws_iam_policy" "deployment_role_prod" {
  name = "rankings-deployment-role-prod-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ProdResources"
        Effect = "Allow"
        Action = [
          "ecs:*",
          "ecr:*",
          "logs:*",
          "scheduler:*",
          "lambda:*",
          "cloudfront:*",
          "route53:*"
        ]
        Resource = ["*"]
        Condition = {
          StringLike = {
            "aws:ResourceTag/Stage" = ["prod", ""]
          }
        }
      },
      {
        Sid    = "ProdS3Data"
        Effect = "Allow"
        Action = ["s3:*"]
        Resource = [
          "arn:aws:s3:::sportnumerics-rankings-bucket-prod",
          "arn:aws:s3:::sportnumerics-rankings-bucket-prod/*"
        ]
      },
      {
        Sid    = "ProdS3State"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = [
          "arn:aws:s3:::sportnumerics-rankings-terraform-state/*/prod.tfstate",
          "arn:aws:s3:::sportnumerics-rankings-terraform-state/*/prod.tfstate.lock.info"
        ]
      },
      {
        Sid    = "S3StateBucket"
        Effect = "Allow"
        Action = ["s3:ListBucket", "s3:GetBucketLocation"]
        Resource = ["arn:aws:s3:::sportnumerics-rankings-terraform-state"]
      },
      {
        Sid    = "UntaggedResources"
        Effect = "Allow"
        Action = [
          "ecs:DescribeClusters",
          "ecs:ListTaskDefinitions",
          "ecs:DescribeTaskDefinition",
          "ecr:GetAuthorizationToken",
          "ecr:DescribeRepositories",
          "logs:DescribeLogGroups",
          "lambda:ListFunctions",
          "cloudfront:ListDistributions",
          "route53:ListHostedZones"
        ]
        Resource = ["*"]
      },
      {
        Sid    = "IAMRoles"
        Effect = "Allow",
        Action = [
          "iam:CreateRole",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePermissionsBoundary"
        ],
        Resource = ["arn:aws:iam::${local.account_id}:role/rankings-*-prod*"],
        Condition = {
          StringEquals = {
            "iam:PermissionsBoundary" = aws_iam_policy.permissions_boundary.arn
          }
        }
      },
      {
        Sid    = "IAMRolesRead"
        Effect = "Allow",
        Action = [
          "iam:TagRole",
          "iam:GetRole",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:ListInstanceProfilesForRole",
          "iam:DeleteRole",
          "iam:PassRole"
        ],
        Resource = ["arn:aws:iam::${local.account_id}:role/rankings-*"]
      },
      {
        Sid    = "IAMPolicies"
        Effect = "Allow",
        Action = [
          "iam:CreatePolicy",
          "iam:DeletePolicy",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:ListPolicyVersions",
          "iam:DeletePolicyVersion",
          "iam:CreatePolicyVersion",
          "iam:TagPolicy"
        ],
        Resource = ["arn:aws:iam::${local.account_id}:policy/rankings-*"]
      }
    ]
  })

  tags = {
    App   = "rankings"
    Stage = "prod"
  }
}

# =============================================================================
# DEV DEPLOYMENT ROLE - any branch can assume
# =============================================================================
resource "aws_iam_role" "deployment_role_dev" {
  name = "rankings-deployment-role-dev"
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
          }
          StringLike : {
            "token.actions.githubusercontent.com:sub" : "repo:sportnumerics/rankings:*"
          }
        }
      }
    ]
  })
  managed_policy_arns = [
    aws_iam_policy.deployment_role_dev.arn
  ]

  tags = {
    App   = "rankings"
    Stage = "dev"
  }
}

resource "aws_iam_policy" "deployment_role_dev" {
  name = "rankings-deployment-role-dev-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DevResources"
        Effect = "Allow"
        Action = [
          "ecs:*",
          "ecr:*",
          "logs:*",
          "scheduler:*",
          "lambda:*",
          "cloudfront:*"
        ]
        Resource = ["*"]
        Condition = {
          StringEquals = {
            "aws:ResourceTag/Stage" = "dev"
          }
        }
      },
      {
        Sid    = "DevS3Data"
        Effect = "Allow"
        Action = ["s3:*"]
        Resource = [
          "arn:aws:s3:::sportnumerics-rankings-bucket-dev",
          "arn:aws:s3:::sportnumerics-rankings-bucket-dev/*"
        ]
      },
      {
        Sid    = "DevS3State"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = [
          "arn:aws:s3:::sportnumerics-rankings-terraform-state/*/dev.tfstate",
          "arn:aws:s3:::sportnumerics-rankings-terraform-state/*/dev.tfstate.lock.info"
        ]
      },
      {
        Sid    = "S3StateBucket"
        Effect = "Allow"
        Action = ["s3:ListBucket", "s3:GetBucketLocation"]
        Resource = ["arn:aws:s3:::sportnumerics-rankings-terraform-state"]
      },
      {
        Sid    = "UntaggedResources"
        Effect = "Allow"
        Action = [
          "ecs:DescribeClusters",
          "ecs:ListTaskDefinitions",
          "ecs:DescribeTaskDefinition",
          "ecr:GetAuthorizationToken",
          "ecr:DescribeRepositories",
          "logs:DescribeLogGroups",
          "lambda:ListFunctions",
          "cloudfront:ListDistributions"
        ]
        Resource = ["*"]
      },
      {
        Sid    = "IAMRoles"
        Effect = "Allow",
        Action = [
          "iam:CreateRole",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePermissionsBoundary"
        ],
        Resource = ["arn:aws:iam::${local.account_id}:role/rankings-*-dev*"],
        Condition = {
          StringEquals = {
            "iam:PermissionsBoundary" = aws_iam_policy.permissions_boundary.arn
          }
        }
      },
      {
        Sid    = "IAMRolesRead"
        Effect = "Allow",
        Action = [
          "iam:TagRole",
          "iam:GetRole",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:ListInstanceProfilesForRole",
          "iam:DeleteRole",
          "iam:PassRole"
        ],
        Resource = ["arn:aws:iam::${local.account_id}:role/rankings-*-dev*"]
      },
      {
        Sid    = "IAMPolicies"
        Effect = "Allow",
        Action = [
          "iam:CreatePolicy",
          "iam:DeletePolicy",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:ListPolicyVersions",
          "iam:DeletePolicyVersion",
          "iam:CreatePolicyVersion",
          "iam:TagPolicy"
        ],
        Resource = ["arn:aws:iam::${local.account_id}:policy/rankings-*-dev*"]
      }
    ]
  })

  tags = {
    App   = "rankings"
    Stage = "dev"
  }
}

# =============================================================================
# LEGACY ROLE - keep for now, remove after migration
# =============================================================================
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
          "ecr:*",
          "scheduler:*",
          "lambda:*",
          "cloudfront:*",
          "route53:*"
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
          "iam:DetachRolePolicy",
          "iam:PutRolePermissionsBoundary"
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
          "iam:DeleteRole",
          "iam:PassRole"
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
          "iam:DeletePolicyVersion",
          "iam:CreatePolicyVersion",
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
