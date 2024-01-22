output "frontend_lambda_url" {
    value = aws_lambda_function_url.lambda.function_url
}