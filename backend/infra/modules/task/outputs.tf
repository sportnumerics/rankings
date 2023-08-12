output "rankings_backend_repository" {
    value = split("/", aws_ecr_repository.rankings_backend.repository_url)[0]
}

output "rankings_backend_image_url" {
    value = local.image_url
}