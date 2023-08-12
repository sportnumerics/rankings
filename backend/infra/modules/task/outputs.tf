output "rankings_backend_repository_url" {
    value = aws_ecr_repository.rankings_backend.repository_url
}

output "rankings_backend_repository" {
    value = split("/", aws_ecr_repository.rankings_backend.repository_url)[0]
}
