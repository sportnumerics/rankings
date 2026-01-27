locals {
  oidc_provider_arn = "arn:aws:iam::265978616089:oidc-provider/token.actions.githubusercontent.com"
  account_id        = "265978616089"
}

# =============================================================================
# PROD DEPLOYMENT ROLE - only production environment can assume
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
            "token.actions.githubusercontent.com:sub" : "repo:sportnumerics/rankings:environment:production"
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
        Sid    = "InfraManagement"
        Effect = "Allow"
        Action = [
          "ecs:*",
          "ecr:*",
          "logs:*",
          "scheduler:*",
          "lambda:*",
          "cloudfront:*",
          "route53:*",
          "events:*"
        ]
        Resource = ["*"]
      },
      {
        Sid    = "ProdS3"
        Effect = "Allow"
        Action = ["s3:*"]
        Resource = [
          "arn:aws:s3:::sportnumerics-rankings-bucket-prod",
          "arn:aws:s3:::sportnumerics-rankings-bucket-prod/*"
        ]
      },
      {
        Sid    = "TerraformState"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket", "s3:GetBucketLocation"]
        Resource = [
          "arn:aws:s3:::sportnumerics-rankings-terraform-state",
          "arn:aws:s3:::sportnumerics-rankings-terraform-state/*"
        ]
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
        Resource = ["arn:aws:iam::${local.account_id}:role/rankings-*"],
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
# DEV DEPLOYMENT ROLE - only dev environment can assume
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
            "token.actions.githubusercontent.com:sub" : "repo:sportnumerics/rankings:environment:dev"
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
        Sid    = "DevResourcesWrite"
        Effect = "Allow"
        Action = [
          # ECS - write actions only
          "ecs:CreateCluster",
          "ecs:DeleteCluster",
          "ecs:UpdateCluster",
          "ecs:RegisterTaskDefinition",
          "ecs:DeregisterTaskDefinition",
          "ecs:RunTask",
          "ecs:StopTask",
          "ecs:UpdateService",
          "ecs:CreateService",
          "ecs:DeleteService",
          "ecs:TagResource",
          "ecs:UntagResource",
          # ECR - write actions only (read actions are in ReadOnly)
          "ecr:CreateRepository",
          "ecr:DeleteRepository",
          "ecr:PutImage",
          "ecr:BatchDeleteImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutLifecyclePolicy",
          "ecr:DeleteLifecyclePolicy",
          "ecr:TagResource",
          "ecr:UntagResource",
          # Logs - write actions only
          "logs:CreateLogGroup",
          "logs:DeleteLogGroup",
          "logs:CreateLogStream",
          "logs:DeleteLogStream",
          "logs:PutLogEvents",
          "logs:PutRetentionPolicy",
          "logs:DeleteRetentionPolicy",
          "logs:TagResource",
          "logs:UntagResource",
          "logs:PutResourcePolicy",
          "logs:DeleteResourcePolicy",
          # Scheduler - write actions only
          "scheduler:CreateSchedule",
          "scheduler:UpdateSchedule",
          "scheduler:DeleteSchedule",
          "scheduler:TagResource",
          "scheduler:UntagResource",
          # Lambda - write actions only
          "lambda:CreateFunction",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:DeleteFunction",
          "lambda:PublishVersion",
          "lambda:CreateAlias",
          "lambda:UpdateAlias",
          "lambda:DeleteAlias",
          "lambda:PutFunctionConcurrency",
          "lambda:DeleteFunctionConcurrency",
          "lambda:AddPermission",
          "lambda:RemovePermission",
          "lambda:TagResource",
          "lambda:UntagResource",
          "lambda:CreateFunctionUrlConfig",
          "lambda:UpdateFunctionUrlConfig",
          "lambda:DeleteFunctionUrlConfig",
          # CloudFront - write actions only
          "cloudfront:CreateDistribution",
          "cloudfront:UpdateDistribution",
          "cloudfront:DeleteDistribution",
          "cloudfront:CreateInvalidation",
          "cloudfront:TagResource",
          "cloudfront:UntagResource",
          "cloudfront:CreateOriginAccessControl",
          "cloudfront:UpdateOriginAccessControl",
          "cloudfront:DeleteOriginAccessControl",
          "cloudfront:CreateCachePolicy",
          "cloudfront:UpdateCachePolicy",
          "cloudfront:DeleteCachePolicy",
          # EventBridge - write actions only
          "events:PutRule",
          "events:DeleteRule",
          "events:EnableRule",
          "events:DisableRule",
          "events:PutTargets",
          "events:RemoveTargets",
          "events:TagResource",
          "events:UntagResource",
          # Route53 - write actions only
          "route53:ChangeResourceRecordSets",
          "route53:CreateHostedZone",
          "route53:DeleteHostedZone",
          "route53:ChangeTagsForResource"
        ]
        Resource = ["*"]
        Condition = {
          StringEquals = {
            "aws:ResourceTag/Stage" = "dev"
          }
        }
      },
      # NOTE: TagResource is needed *before* a resource has Stage=dev, so it cannot
      # be protected with aws:ResourceTag/Stage. Instead, constrain it by the tags
      # being applied.
      {
        Sid    = "DevLambdaTagResource"
        Effect = "Allow"
        Action = [
          "lambda:TagResource",
          "lambda:UntagResource"
        ]
        # Scope to *dev* Lambdas by name to avoid retagging prod resources.
        # (Lambda ARN wildcards are supported in IAM resource statements.)
        Resource = ["arn:aws:lambda:us-west-2:${local.account_id}:function:*-dev"],
        Condition = {
          StringEquals = {
            "aws:RequestTag/Stage" = "dev"
          }
          "ForAllValues:StringEquals" = {
            "aws:TagKeys" = ["Stage", "App"]
          }
        }
      },
      {
        Sid    = "ReadOnly"
        Effect = "Allow"
        Action = [
          # ECS
          "ecs:Describe*",
          "ecs:List*",
          # ECR
          "ecr:GetAuthorizationToken",
          "ecr:Describe*",
          "ecr:List*",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          # Logs
          "logs:Describe*",
          "logs:List*",
          "logs:Get*",
          # Lambda
          "lambda:Get*",
          "lambda:List*",
          # CloudFront
          "cloudfront:Get*",
          "cloudfront:List*",
          # Scheduler
          "scheduler:Get*",
          "scheduler:List*",
          # Events
          "events:Describe*",
          "events:List*",
          # Route53
          "route53:Get*",
          "route53:List*",
          "route53:TestDNSAnswer"
        ]
        Resource = ["*"]
      },
      {
        Sid    = "DevS3"
        Effect = "Allow"
        Action = ["s3:*"]
        Resource = [
          "arn:aws:s3:::sportnumerics-rankings-bucket-dev",
          "arn:aws:s3:::sportnumerics-rankings-bucket-dev/*"
        ]
      },
      {
        Sid    = "TerraformState"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket", "s3:GetBucketLocation"]
        Resource = [
          "arn:aws:s3:::sportnumerics-rankings-terraform-state",
          "arn:aws:s3:::sportnumerics-rankings-terraform-state/*"
        ]
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
