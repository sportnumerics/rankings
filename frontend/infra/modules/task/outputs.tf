output "cloudfront_domain" {
    value = aws_cloudfront_distribution.frontend.domain_name
}

output "cloudfront_distribution_id" {
    value = aws_cloudfront_distribution.frontend.id
}