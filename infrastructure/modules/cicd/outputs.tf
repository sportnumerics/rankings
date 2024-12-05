output "rankings_deployment_role_arn" {
  value = aws_iam_role.deployment_role.arn
}

output "rankings_deployment_permissions_boundary_arn" {
  value = aws_iam_policy.permissions_boundary.arn
}
