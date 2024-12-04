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
          "s3:*"
        ]
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
